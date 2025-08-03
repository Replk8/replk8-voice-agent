import os
import logging
from typing import Dict, Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CustomerProfile:
    phone_number: str
    business_name: str
    subscription_tier: Literal["basic", "premium", "enterprise"]
    tts_preference: Literal["polly", "elevenlabs"]
    language: str = "en-US"
    voice_id: Optional[str] = None
    business_context: Optional[Dict] = None

class CustomerService:
    def __init__(self):
        # In production, this would connect to your database
        # For demo purposes, using in-memory storage
        self.customers = {}
        self._load_demo_customers()
    
    def _load_demo_customers(self):
        """Load demo customer data"""
        demo_customers = [
            CustomerProfile(
                phone_number="+1234567890",
                business_name="Demo Salon",
                subscription_tier="basic",
                tts_preference="polly",
                language="en-US",
                business_context={
                    "name": "Beautiful Hair Salon",
                    "services": ["Haircut", "Color", "Styling", "Manicure"],
                    "address": "123 Main St, Your City",
                    "phone": "+1234567890"
                }
            ),
            CustomerProfile(
                phone_number="+0987654321", 
                business_name="Premium Spa",
                subscription_tier="premium",
                tts_preference="elevenlabs",
                language="en-US",
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                business_context={
                    "name": "Luxury Day Spa",
                    "services": ["Massage", "Facial", "Body Wrap", "Manicure", "Pedicure"],
                    "address": "456 Spa Avenue, Your City", 
                    "phone": "+0987654321"
                }
            )
        ]
        
        for customer in demo_customers:
            self.customers[customer.phone_number] = customer
    
    def get_customer_profile(self, phone_number: str) -> Optional[CustomerProfile]:
        """Get customer profile by phone number"""
        return self.customers.get(phone_number)
    
    def get_tts_service_for_customer(self, phone_number: str) -> str:
        """Determine which TTS service to use for a customer"""
        customer = self.get_customer_profile(phone_number)
        
        if not customer:
            # Default for unknown customers
            return "polly"
        
        # Business logic for TTS selection
        if customer.subscription_tier == "enterprise":
            return customer.tts_preference
        elif customer.subscription_tier == "premium":
            return "elevenlabs" if customer.tts_preference == "elevenlabs" else "polly"
        else:  # basic tier
            return "polly"  # Basic customers always get Polly
    
    def get_voice_settings(self, phone_number: str) -> Dict:
        """Get voice settings for a customer"""
        customer = self.get_customer_profile(phone_number)
        
        if not customer:
            return {
                "service": "polly",
                "voice_id": None,
                "language": "en-US"
            }
        
        tts_service = self.get_tts_service_for_customer(phone_number)
        
        return {
            "service": tts_service,
            "voice_id": customer.voice_id,
            "language": customer.language
        }
    
    def get_business_context(self, phone_number: str) -> Optional[Dict]:
        """Get business context for AI responses"""
        customer = self.get_customer_profile(phone_number)
        return customer.business_context if customer else None
    
    def update_customer_preferences(
        self, 
        phone_number: str, 
        tts_preference: Optional[str] = None,
        voice_id: Optional[str] = None,
        language: Optional[str] = None
    ):
        """Update customer TTS preferences"""
        customer = self.get_customer_profile(phone_number)
        if customer:
            if tts_preference:
                customer.tts_preference = tts_preference
            if voice_id:
                customer.voice_id = voice_id
            if language:
                customer.language = language
            
            logger.info(f"Updated preferences for {phone_number}")
        else:
            logger.warning(f"Customer not found: {phone_number}")
    
    def can_use_premium_tts(self, phone_number: str) -> bool:
        """Check if customer can use premium TTS (Eleven Labs)"""
        customer = self.get_customer_profile(phone_number)
        if not customer:
            return False
        
        return customer.subscription_tier in ["premium", "enterprise"]
    
    def get_available_voices_for_customer(self, phone_number: str) -> Dict:
        """Get available voices based on customer's subscription"""
        customer = self.get_customer_profile(phone_number)
        tts_service = self.get_tts_service_for_customer(phone_number)
        
        from services.tts_service import TTSService
        tts = TTSService()
        
        available_voices = tts.get_available_voices(tts_service)
        
        return {
            "service": tts_service,
            "subscription_tier": customer.subscription_tier if customer else "basic",
            "voices": available_voices
        }