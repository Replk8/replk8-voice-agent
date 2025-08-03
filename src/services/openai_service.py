import os
import openai
import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Conversation history storage (in production, use Redis or database)
        self.conversations = {}
    
    async def generate_response(
        self, 
        user_input: str, 
        call_control_id: str,
        business_context: Optional[Dict] = None,
        language: str = "en"
    ) -> str:
        """Generate AI response using GPT-4"""
        try:
            # Get or create conversation history
            if call_control_id not in self.conversations:
                self.conversations[call_control_id] = []
            
            conversation_history = self.conversations[call_control_id]
            
            # Build system prompt based on business context
            system_prompt = self._build_system_prompt(business_context, language)
            
            # Prepare messages for GPT-4
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep only last 10 exchanges to manage token usage
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                self.conversations[call_control_id] = conversation_history
            
            logger.info(f"Generated AI response: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I apologize, I'm having trouble processing your request. Could you please repeat that?"
    
    def _build_system_prompt(self, business_context: Optional[Dict] = None, language: str = "en") -> str:
        """Build system prompt based on business context and language"""
        
        base_prompts = {
            "en": """You are a professional AI assistant for appointment scheduling and customer service. 
            
Your primary functions:
1. Answer questions about services, pricing, and availability
2. Schedule, reschedule, or cancel appointments
3. Provide business information (hours, location, policies)
4. Handle customer inquiries professionally and helpfully

Guidelines:
- Be friendly, professional, and concise
- Ask clarifying questions when needed
- If you need to schedule an appointment, collect: name, phone, preferred date/time, service type
- If you can't help with something, offer to transfer to a human
- Keep responses under 2 sentences when possible for phone conversations
- Always confirm important details back to the customer

Business hours: Monday-Saturday 9 AM - 7 PM, Closed Sunday""",
            
            "es": """Eres un asistente de IA profesional para programar citas y servicio al cliente.

Tus funciones principales:
1. Responder preguntas sobre servicios, precios y disponibilidad
2. Programar, reprogramar o cancelar citas
3. Proporcionar información del negocio (horarios, ubicación, políticas) 
4. Manejar consultas de clientes de manera profesional y útil

Pautas:
- Sé amigable, profesional y conciso
- Haz preguntas aclaratorias cuando sea necesario
- Para programar citas, recopila: nombre, teléfono, fecha/hora preferida, tipo de servicio
- Si no puedes ayudar con algo, ofrece transferir a una persona
- Mantén respuestas bajo 2 oraciones para conversaciones telefónicas
- Siempre confirma detalles importantes con el cliente

Horario: Lunes-Sábado 9 AM - 7 PM, Cerrado Domingo"""
        }
        
        system_prompt = base_prompts.get(language, base_prompts["en"])
        
        # Add business-specific context if provided
        if business_context:
            business_info = f"""
            
Business Information:
- Name: {business_context.get('name', 'Our Business')}
- Services: {', '.join(business_context.get('services', []))}
- Location: {business_context.get('address', 'Please ask for location')}
- Phone: {business_context.get('phone', '')}
"""
            system_prompt += business_info
        
        return system_prompt
    
    async def extract_appointment_details(self, conversation_text: str) -> Dict:
        """Extract appointment details from conversation using GPT-4"""
        try:
            extraction_prompt = """
Extract appointment booking details from this conversation. Return JSON with these fields:
- name: customer name
- phone: phone number  
- service: requested service
- date: preferred date (YYYY-MM-DD format if mentioned)
- time: preferred time (24-hour format if mentioned)
- notes: any special requests or notes

Conversation: {conversation_text}

Return only valid JSON, no other text:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user", 
                    "content": extraction_prompt.format(conversation_text=conversation_text)
                }],
                max_tokens=200,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Extracted appointment details: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting appointment details: {str(e)}")
            return {}
    
    def clear_conversation(self, call_control_id: str):
        """Clear conversation history for a call"""
        if call_control_id in self.conversations:
            del self.conversations[call_control_id]