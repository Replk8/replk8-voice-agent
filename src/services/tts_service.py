import os
import boto3
import tempfile
import logging
from typing import Optional, Literal
import aiofiles

# Try to import Eleven Labs, skip if not available
try:
    from elevenlabs import generate, Voice
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("WARNING: Eleven Labs not available - premium TTS will be disabled")

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        # Amazon Polly setup
        self.polly_client = boto3.client(
            'polly',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        
        # Eleven Labs setup
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if self.elevenlabs_api_key:
            os.environ["ELEVENLABS_API_KEY"] = self.elevenlabs_api_key
    
    async def generate_speech(
        self, 
        text: str, 
        service: Literal["polly", "elevenlabs"] = "polly",
        voice_id: Optional[str] = None,
        language: str = "en-US"
    ) -> str:
        """Generate speech using either Polly (basic) or Eleven Labs (premium)"""
        
        if service == "polly":
            return await self._generate_polly_speech(text, voice_id, language)
        elif service == "elevenlabs":
            return await self._generate_elevenlabs_speech(text, voice_id)
        else:
            raise ValueError(f"Unsupported TTS service: {service}")
    
    async def _generate_polly_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None,
        language: str = "en-US"
    ) -> str:
        """Generate speech using Amazon Polly"""
        try:
            # Default voices by language
            default_voices = {
                "en-US": "Joanna",
                "es-ES": "Lucia",
                "es-MX": "Mia"
            }
            
            voice = voice_id or default_voices.get(language, "Joanna")
            
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice,
                Engine='neural' if voice in ['Joanna', 'Matthew', 'Lucia'] else 'standard'
            )
            
            # Save to temporary file and return URL/path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(response['AudioStream'].read())
                temp_file_path = temp_file.name
            
            logger.info(f"Generated Polly speech: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Error generating Polly speech: {str(e)}")
            raise
    
    async def _generate_elevenlabs_speech(
        self, 
        text: str, 
        voice_id: Optional[str] = None
    ) -> str:
        """Generate speech using Eleven Labs"""
        try:
            if not ELEVENLABS_AVAILABLE:
                raise ValueError("Eleven Labs SDK not available - falling back to Polly")
            
            if not self.elevenlabs_api_key:
                raise ValueError("ELEVENLABS_API_KEY is required for premium TTS")
            
            # Default to a high-quality voice
            voice = voice_id or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
            
            audio = generate(
                text=text,
                voice=Voice(voice_id=voice),
                model="eleven_monolingual_v1"
            )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio)
                temp_file_path = temp_file.name
            
            logger.info(f"Generated Eleven Labs speech: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            logger.error(f"Error generating Eleven Labs speech: {str(e)}")
            # Fall back to Polly if Eleven Labs fails
            logger.info("Falling back to Amazon Polly")
            return await self._generate_polly_speech(text, voice_id)
    
    def get_available_voices(self, service: str = "polly") -> dict:
        """Get available voices for the specified service"""
        if service == "polly":
            return {
                "en-US": ["Joanna", "Matthew", "Ivy", "Justin", "Kendra", "Kimberly", "Salli"],
                "es-ES": ["Lucia", "Enrique"],
                "es-MX": ["Mia"]
            }
        elif service == "elevenlabs":
            return {
                "premium": [
                    {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
                    {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi"},
                    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
                    {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni"},
                    {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli"},
                    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"}
                ]
            }
        else:
            return {}