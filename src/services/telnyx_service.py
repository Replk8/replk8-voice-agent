import os
import telnyx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TelnyxService:
    def __init__(self):
        self.api_key = os.getenv("TELNYX_API_KEY")
        if not self.api_key:
            raise ValueError("TELNYX_API_KEY environment variable is required")
        
        telnyx.api_key = self.api_key
    
    async def answer_call(self, call_control_id: str) -> dict:
        """Answer an incoming call"""
        try:
            result = telnyx.Call.answer(call_control_id)
            logger.info(f"Answered call: {call_control_id}")
            return result
        except Exception as e:
            logger.error(f"Error answering call: {str(e)}")
            raise
    
    async def hangup_call(self, call_control_id: str) -> dict:
        """Hangup a call"""
        try:
            result = telnyx.Call.hangup(call_control_id)
            logger.info(f"Hung up call: {call_control_id}")
            return result
        except Exception as e:
            logger.error(f"Error hanging up call: {str(e)}")
            raise
    
    async def play_audio(self, call_control_id: str, media_url: str) -> dict:
        """Play audio file to the caller"""
        try:
            result = telnyx.Call.playback_start(
                call_control_id, 
                media_url=media_url
            )
            logger.info(f"Playing audio on call {call_control_id}: {media_url}")
            return result
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            raise
    
    async def speak_text(self, call_control_id: str, text: str, voice: str = "female") -> dict:
        """Use Telnyx built-in TTS to speak text"""
        try:
            result = telnyx.Call.speak(
                call_control_id,
                payload=text,
                voice=voice,
                language="en-US"
            )
            logger.info(f"Speaking text on call {call_control_id}: {text[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error speaking text: {str(e)}")
            raise
    
    async def start_recording(self, call_control_id: str, channels: str = "single") -> dict:
        """Start recording the call"""
        try:
            result = telnyx.Call.record_start(
                call_control_id,
                channels=channels,
                format="mp3"
            )
            logger.info(f"Started recording call: {call_control_id}")
            return result
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            raise
    
    async def stop_recording(self, call_control_id: str) -> dict:
        """Stop recording the call"""
        try:
            result = telnyx.Call.record_stop(call_control_id)
            logger.info(f"Stopped recording call: {call_control_id}")
            return result
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            raise
    
    async def gather_input(
        self, 
        call_control_id: str, 
        prompt: str,
        max_digits: int = 1,
        timeout_millis: int = 5000
    ) -> dict:
        """Gather DTMF input from caller"""
        try:
            result = telnyx.Call.gather_using_speak(
                call_control_id,
                payload=prompt,
                max_digits=max_digits,
                timeout_millis=timeout_millis,
                voice="female"
            )
            logger.info(f"Gathering input on call {call_control_id}")
            return result
        except Exception as e:
            logger.error(f"Error gathering input: {str(e)}")
            raise
    
    async def make_outbound_call(
        self, 
        to_number: str, 
        from_number: str,
        webhook_url: Optional[str] = None
    ) -> dict:
        """Make an outbound call"""
        try:
            result = telnyx.Call.create(
                connection_id=os.getenv("TELNYX_CONNECTION_ID"),
                to=to_number,
                from_=from_number,
                webhook_url=webhook_url or os.getenv("TELNYX_WEBHOOK_URL")
            )
            logger.info(f"Making outbound call from {from_number} to {to_number}")
            return result
        except Exception as e:
            logger.error(f"Error making outbound call: {str(e)}")
            raise