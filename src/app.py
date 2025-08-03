from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging

from services.telnyx_service import TelnyxService
from services.deepgram_service import DeepgramService
from services.tts_service import TTSService
from services.openai_service import OpenAIService
from services.customer_service import CustomerService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Replk8 AI Voice Agent", version="1.0.0")

# Initialize services
telnyx_service = TelnyxService()
deepgram_service = DeepgramService()
tts_service = TTSService()
openai_service = OpenAIService()
customer_service = CustomerService()

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
    
    # Get customer-specific voice settings
    voice_settings = customer_service.get_voice_settings(from_number)
    business_context = customer_service.get_business_context(from_number)
    
    # Personalized greeting based on business context
    if business_context:
        greeting = f"Hello! Thank you for calling {business_context['name']}. How can I help you today?"
    else:
        greeting = "Hello! Thank you for calling. How can I help you today?"
    
    # Generate TTS audio using customer's preferred service
    audio_url = await tts_service.generate_speech(
        greeting, 
        service=voice_settings["service"],
        voice_id=voice_settings["voice_id"],
        language=voice_settings["language"]
    )
    
    # Play the greeting
    await telnyx_service.play_audio(call_control_id, audio_url)
    
    # Start listening for speech
    await telnyx_service.start_recording(call_control_id)
    
    return JSONResponse(content={"status": "ok"})

async def handle_recording_saved(payload):
    """Handle saved recording for speech processing"""
    call_control_id = payload["data"]["payload"]["call_control_id"]
    recording_url = payload["data"]["payload"]["recording_urls"]["mp3"]
    from_number = payload["data"]["payload"].get("from", "")
    
    # Transcribe the audio using Deepgram
    transcript = await deepgram_service.transcribe_audio(recording_url)
    
    if transcript:
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
        
        # Convert response to speech using customer's TTS preference
        audio_url = await tts_service.generate_speech(
            ai_response, 
            service=voice_settings["service"],
            voice_id=voice_settings["voice_id"],
            language=voice_settings["language"]
        )
        
        # Play the AI response
        await telnyx_service.play_audio(call_control_id, audio_url)
        
        # Continue listening
        await telnyx_service.start_recording(call_control_id)
    
    return JSONResponse(content={"status": "ok"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)