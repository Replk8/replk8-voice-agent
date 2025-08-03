import os
import httpx
import logging

from deepgram import DeepgramClient, PrerecordedOptions

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
        
        self.client = DeepgramClient(self.api_key)
    
    async def transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio from URL using Deepgram"""
        try:
            # Download audio file
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(audio_url)
                response.raise_for_status()
                audio_data = response.content
            
            # Configure Deepgram options
            options = PrerecordedOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                punctuate=True,
                diarize=False,
                multichannel=False
            )
            
            # Send audio to Deepgram
            response = self.client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_data, "mimetype": "audio/mp3"}, 
                options
            )
            
            # Extract transcript
            if response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                logger.info(f"Transcribed: {transcript}")
                return transcript.strip()
            else:
                logger.warning("No transcript found in response")
                return ""
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""
    
    async def transcribe_realtime(self, audio_stream):
        """For future real-time transcription implementation"""
        # This would be used for streaming audio transcription
        pass