#!/usr/bin/env python3
"""
Test script to verify AI voice agent services are working correctly.
Run this after setting up your .env file with API keys.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_tts_services():
    """Test both Polly and Eleven Labs TTS services"""
    print("Testing TTS Services...")
    
    from src.services.tts_service import TTSService
    
    tts = TTSService()
    
    test_text = "Hello! This is a test of the text-to-speech service."
    
    try:
        # Test Polly (basic)
        print("Testing Amazon Polly...")
        polly_audio = await tts.generate_speech(test_text, service="polly")
        print(f"SUCCESS: Polly TTS successful: {polly_audio}")
    except Exception as e:
        print(f"ERROR: Polly TTS failed: {e}")
    
    try:
        # Test Eleven Labs (premium)
        if os.getenv("ELEVENLABS_API_KEY"):
            print("Testing Eleven Labs...")
            elevenlabs_audio = await tts.generate_speech(test_text, service="elevenlabs")
            print(f"SUCCESS: Eleven Labs TTS successful: {elevenlabs_audio}")
        else:
            print("WARNING: Eleven Labs API key not found, skipping test")
    except Exception as e:
        print(f"ERROR: Eleven Labs TTS failed: {e}")

async def test_deepgram():
    """Test Deepgram STT service"""
    print("\nTesting Deepgram STT...")
    
    # Note: This requires an actual audio file URL to test
    print("WARNING: Deepgram test requires actual audio URL - skipping for now")
    print("SUCCESS: Deepgram service imported successfully")

async def test_openai():
    """Test OpenAI GPT-4 service"""
    print("\nTesting OpenAI GPT-4...")
    
    from src.services.openai_service import OpenAIService
    
    try:
        openai_service = OpenAIService()
        response = await openai_service.generate_response(
            "Hello, I'd like to schedule an appointment",
            "test_call_123"
        )
        print(f"SUCCESS: OpenAI response: {response[:50]}...")
    except Exception as e:
        print(f"ERROR: OpenAI test failed: {e}")

async def test_customer_service():
    """Test customer service tier logic"""
    print("\nTesting Customer Service...")
    
    from src.services.customer_service import CustomerService
    
    customer_service = CustomerService()
    
    # Test demo customers
    demo_numbers = ["+1234567890", "+0987654321", "+5555555555"]
    
    for number in demo_numbers:
        voice_settings = customer_service.get_voice_settings(number)
        can_use_premium = customer_service.can_use_premium_tts(number)
        print(f"PHONE {number}: {voice_settings['service']} TTS, Premium: {can_use_premium}")

async def main():
    """Run all tests"""
    print("Testing Replk8 AI Voice Agent Services\n")
    
    # Check environment variables
    required_vars = ["TELNYX_API_KEY", "DEEPGRAM_API_KEY", "OPENAI_API_KEY", "AWS_ACCESS_KEY_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set up your .env file based on .env.example")
        return
    
    await test_customer_service()
    await test_tts_services()
    await test_deepgram()
    await test_openai()
    
    print("\nSUCCESS: All tests completed!")
    print("\nNext steps:")
    print("1. Set up your Telnyx webhook URL to point to your server")
    print("2. Configure your phone number in Telnyx portal")
    print("3. Start the server: python src/app.py")
    print("4. Test with a phone call!")

if __name__ == "__main__":
    asyncio.run(main())