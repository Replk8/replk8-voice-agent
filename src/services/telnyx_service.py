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
            # Use the correct Telnyx API method
            call = telnyx.Call()
            call.call_control_id = call_control_id
            result = call.answer()
            logger.info(f"Answered call: {call_control_id}")
            return {"status": "answered", "call_control_id": call_control_id}
        except Exception as e:
            logger.error(f"Error answering call: {str(e)}")
            # Try alternative approach
            try:
                import requests
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                response = requests.post(
                    f'https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer',
                    headers=headers
                )
                logger.info(f"Answered call via direct API: {call_control_id}")
                return {"status": "answered", "call_control_id": call_control_id}
            except Exception as e2:
                logger.error(f"Error with direct API call: {str(e2)}")
                raise
    
    async def hangup_call(self, call_control_id: str) -> dict:
        """Hangup a call"""
        try:
            result = telnyx.Call.hangup(call_control_id)
            logger.info(f"Hung up call: {call_control_id}")
            return {"status": "hung_up", "call_control_id": call_control_id}
        except Exception as e:
            logger.error(f"Error hanging up call: {str(e)}")
            raise
    
    async def play_audio(self, call_control_id: str, media_url: str) -> dict:
        """Play audio file to the caller"""
        try:
            # Try direct API approach first
            import requests
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'media_url': media_url
            }
            response = requests.post(
                f'https://api.telnyx.com/v2/calls/{call_control_id}/actions/playback_start',
                headers=headers,
                json=data
            )
            logger.info(f"Playing audio on call {call_control_id}: {media_url}")
            return {"status": "playing", "call_control_id": call_control_id}
        except Exception as e:
            logger.error(f"Error playing audio: {str(e)}")
            raise
    
    async def speak_text(self, call_control_id: str, text: str, voice: str = "female") -> dict:
        """Use Telnyx built-in TTS to speak text"""
        try:
            # Use direct API approach
            import requests
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'payload': text,
                'voice': voice,
                'language': 'en-US'
            }
            response = requests.post(
                f'https://api.telnyx.com/v2/calls/{call_control_id}/actions/speak',
                headers=headers,
                json=data
            )
            logger.info(f"Speaking text on call {call_control_id}: {text[:50]}...")
            return {"status": "speaking", "call_control_id": call_control_id}
        except Exception as e:
            logger.error(f"Error speaking text: {str(e)}")
            raise
    
    async def start_recording(self, call_control_id: str, channels: str = "single") -> dict:
        """Start recording the call"""
        try:
            # Use direct API approach
            import requests
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'channels': channels,
                'format': 'mp3'
            }
            response = requests.post(
                f'https://api.telnyx.com/v2/calls/{call_control_id}/actions/record_start',
                headers=headers,
                json=data
            )
            logger.info(f"Started recording call: {call_control_id}")
            return {"status": "recording", "call_control_id": call_control_id}
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            raise
    
    async def stop_recording(self, call_control_id: str) -> dict:
        """Stop recording the call"""
        try:
            # Use direct API approach
            import requests
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f'https://api.telnyx.com/v2/calls/{call_control_id}/actions/record_stop',
                headers=headers
            )
            logger.info(f"Stopped recording call: {call_control_id}")
            return {"status": "stopped", "call_control_id": call_control_id}
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