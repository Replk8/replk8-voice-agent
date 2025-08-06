from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import logging
import asyncio

from services.telnyx_service import TelnyxService
from services.deepgram_service import DeepgramService
from services.tts_service import TTSService
from services.openai_service import OpenAIService
from services.customer_service import CustomerService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Replk8 AI Voice Agent", version="1.0.0")

# Add CORS middleware for web widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
telnyx_service = TelnyxService()
deepgram_service = DeepgramService()
tts_service = TTSService()
openai_service = OpenAIService()
customer_service = CustomerService()

# Track call states to prevent duplicate processing
call_states = {}

@app.get("/")
async def root():
    return {"message": "Replk8 AI Voice Agent is running"}

@app.post("/webhooks/telnyx")
async def telnyx_webhook(request: Request):
    """Handle incoming Telnyx webhooks"""
    try:
        payload = await request.json()
        event_type = payload.get("data", {}).get("event_type")
        
        logger.info(f"Received Telnyx webhook: {event_type}")
        
        if event_type == "call.initiated":
            return await handle_call_initiated(payload)
        elif event_type == "call.answered":
            return await handle_call_answered(payload)
        elif event_type == "call.recording.saved":
            return await handle_recording_saved(payload)
        elif event_type == "call.speak.started":
            logger.info("Call speak started")
            return JSONResponse(content={"status": "ok"})
        elif event_type == "call.speak.ended":
            return await handle_speak_ended(payload)
        elif event_type == "call.hangup":
            return await handle_call_hangup(payload)
        else:
            logger.warning(f"Unhandled event type: {event_type}")
            return JSONResponse(content={"status": "ok"})
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_call_initiated(payload):
    """Handle incoming call initiation"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    from_number = payload["data"]["payload"]["from"]
    
    logger.info(f"Call initiated from {from_number}, call_control_id: {call_control_id}")
    
    # Answer the call
    await telnyx_service.answer_call(call_control_id)
    
    return JSONResponse(content={"status": "ok"})

async def handle_call_answered(payload):
    """Handle call answered event"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    from_number = payload["data"]["payload"]["from"]
    
    # Prevent duplicate processing
    if call_control_id in call_states and call_states[call_control_id].get("answered"):
        logger.info(f"Call {call_control_id} already answered, skipping")
        return JSONResponse(content={"status": "ok"})
    
    # Mark as answered
    call_states[call_control_id] = {
        "answered": True, 
        "greeting_spoken": False,
        "conversation_turn": 0,
        "last_response_time": None
    }
    
    # Get customer-specific voice settings
    voice_settings = customer_service.get_voice_settings(from_number)
    business_context = customer_service.get_business_context(from_number)
    
    # Personalized greeting based on business context
    if business_context:
        greeting = f"Hello! Thank you for calling {business_context['name']}. How can I help you today?"
    else:
        greeting = "Hello! Thank you for calling. How can I help you today?"
    
    # Use Telnyx built-in TTS for now (more reliable than file upload)
    await telnyx_service.speak_text(call_control_id, greeting)
    call_states[call_control_id]["greeting_spoken"] = True
    
    return JSONResponse(content={"status": "ok"})

async def handle_recording_saved(payload):
    """Handle saved recording for speech processing"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    recording_url = payload["data"]["payload"]["recording_urls"]["mp3"]
    from_number = payload["data"]["payload"].get("from", "")
    
    # Check if we're in a conversation loop
    if call_control_id in call_states:
        call_state = call_states[call_control_id]
        call_state["conversation_turn"] += 1
        
        # Prevent infinite loops - limit conversation turns
        if call_state["conversation_turn"] > 10:
            logger.warning(f"Call {call_control_id} exceeded conversation limit, ending call")
            await telnyx_service.speak_text(call_control_id, "I apologize, but I need to transfer you to a human agent. Thank you for calling.")
            await telnyx_service.hangup_call(call_control_id)
            return JSONResponse(content={"status": "ok"})
    
    # Transcribe the audio using Deepgram
    transcript = await deepgram_service.transcribe_audio(recording_url)
    
    logger.info(f"Transcribed text: '{transcript}' (length: {len(transcript) if transcript else 0})")
    
    if transcript and len(transcript.strip()) > 3:  # Only process if there's meaningful speech
        # Get customer context and voice settings
        voice_settings = customer_service.get_voice_settings(from_number)
        business_context = customer_service.get_business_context(from_number)
        language = voice_settings["language"][:2]  # Extract language code (en, es)
        
        # Generate AI response using GPT-4 with business context
        ai_response = await openai_service.generate_response(
            transcript, 
            call_control_id,
            business_context,
            language
        )
        
        # Validate response length and content
        if ai_response and len(ai_response.strip()) > 10:
            # Use Telnyx built-in TTS for AI responses (more reliable)
            await telnyx_service.speak_text(call_control_id, ai_response)
            
            # Continue listening with shorter delay
            await asyncio.sleep(1)  # Reduced from 5 seconds
            await telnyx_service.start_recording(call_control_id)
        else:
            # If AI response is too short, give a default response
            await telnyx_service.speak_text(call_control_id, "I didn't catch that. Could you please repeat?")
            await asyncio.sleep(1)
            await telnyx_service.start_recording(call_control_id)
    else:
        # No meaningful speech detected - give helpful prompts
        if call_control_id in call_states:
            call_state = call_states[call_control_id]
            if call_state.get("conversation_turn", 0) == 1:
                # First attempt - gentle prompt
                await telnyx_service.speak_text(call_control_id, "I didn't hear anything. Could you please speak up or say hello?")
            elif call_state.get("conversation_turn", 0) == 2:
                # Second attempt - more specific
                await telnyx_service.speak_text(call_control_id, "I'm still not hearing you. You can ask me about appointments, business hours, or services. Please speak clearly.")
            else:
                # Third attempt - offer help
                await telnyx_service.speak_text(call_control_id, "I'm having trouble hearing you. You can say things like 'schedule appointment' or 'business hours'. Please try again.")
        
        await asyncio.sleep(1)
        await telnyx_service.start_recording(call_control_id)
    
    return JSONResponse(content={"status": "ok"})

async def handle_speak_ended(payload):
    """Handle when TTS finishes speaking"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    
    # Only start recording after the greeting is done
    if call_control_id in call_states and call_states[call_control_id].get("greeting_spoken"):
        logger.info(f"Greeting finished, starting recording for call {call_control_id}")
        await telnyx_service.start_recording(call_control_id)
        call_states[call_control_id]["listening"] = True
        
        # Give users more time to speak - increased from 3 to 5 seconds
        asyncio.create_task(check_for_speech(call_control_id, 5))
    
    return JSONResponse(content={"status": "ok"})

async def handle_call_hangup(payload):
    """Handle call hangup"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    
    # Clean up call state
    if call_control_id in call_states:
        del call_states[call_control_id]
    
    # Clear conversation history
    openai_service.clear_conversation(call_control_id)
    
    logger.info(f"Call ended: {call_control_id}")
    return JSONResponse(content={"status": "ok"})

async def check_for_speech(call_control_id: str, delay_seconds: int):
    """Check for speech after a delay and process it"""
    await asyncio.sleep(delay_seconds)
    
    # Check if call is still active
    if call_control_id not in call_states:
        return
    
    try:
        # Stop recording to trigger processing
        await telnyx_service.stop_recording(call_control_id)
        logger.info(f"Stopped recording for call {call_control_id} to trigger processing")
    except Exception as e:
        logger.error(f"Error stopping recording: {str(e)}")

# TTS Demo Endpoints
@app.get("/demo")
async def tts_demo_page():
    """Serve the TTS demo widget page"""
    return FileResponse("tts_demo_widget.html")

@app.post("/api/tts/generate")
async def generate_tts(request: Request):
    """Generate TTS audio for the demo widget"""
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        service = data.get("service", "polly")
        voice_id = data.get("voice_id")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        if not voice_id:
            raise HTTPException(status_code=400, detail="Voice ID is required")
        
        # Generate speech using the TTS service
        audio_file_path = await tts_service.generate_speech(
            text=text,
            service=service,
            voice_id=voice_id
        )
        
        # Return the file path (in production, you'd serve this from a CDN)
        return JSONResponse(content={
            "audio_url": f"/api/tts/audio/{os.path.basename(audio_file_path)}",
            "file_path": audio_file_path
        })
        
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tts/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files"""
    try:
        # Security: only allow .mp3 files
        if not filename.endswith('.mp3'):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        file_path = os.path.join("/tmp", filename)  # Assuming files are saved in /tmp
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error serving audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)