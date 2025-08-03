# Replk8 AI Voice Agent

A flexible AI voice agent platform that automates appointment scheduling, customer communication, and knowledge delivery over phone and SMS using Telnyx, built with FastAPI.

## 🎯 Features

- **Inbound AI Calls**: Natural voice agent that answers calls, greets customers, and handles conversations
- **Dual TTS System**: Amazon Polly (basic) + Eleven Labs (premium) based on customer tiers
- **Smart Speech Processing**: Deepgram STT → GPT-4 → TTS pipeline
- **Customer-Aware Routing**: Personalized greetings and TTS selection by subscription tier
- **Business Context Integration**: Customizable knowledge base per business
- **Multilingual Support**: English and Spanish ready

## 🛠 Tech Stack

- **Backend**: FastAPI + Python
- **Telephony**: Telnyx (Voice + SMS)
- **Speech-to-Text**: Deepgram
- **AI**: OpenAI GPT-4
- **Text-to-Speech**: Amazon Polly + Eleven Labs
- **Cloud**: AWS (Polly, S3)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telnyx account with phone number
- API keys for: Deepgram, OpenAI, AWS, (optional) Eleven Labs

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/replk8-voice-agent.git
   cd replk8-voice-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the server:**
   ```bash
   python src/app.py
   ```

### Deployment on EC2

1. **Clone on your EC2 instance:**
   ```bash
   git clone https://github.com/yourusername/replk8-voice-agent.git
   cd replk8-voice-agent
   ```

2. **Install Python dependencies:**
   ```bash
   sudo yum update -y
   sudo yum install -y python3 python3-pip
   pip3 install --user -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Add your API keys
   ```

4. **Open port 8000 in Security Group**

5. **Start the service:**
   ```bash
   python3 src/app.py
   ```

## 📞 Telnyx Configuration

1. **Set up webhook in Telnyx Portal:**
   - Go to Voice > SIP Connections
   - Set Webhook URL: `http://your-server-ip:8000/webhooks/telnyx`
   - Set API Version: `2`

2. **Assign phone number to SIP connection**

## 🎛 Customer Tiers

- **Basic**: Amazon Polly TTS (cost-effective)
- **Premium**: Eleven Labs TTS (high-quality voices) 
- **Enterprise**: Customer choice of TTS service

## 📁 Project Structure

```
src/
├── app.py                 # FastAPI main application
├── services/
│   ├── telnyx_service.py     # Telnyx call handling
│   ├── deepgram_service.py   # Speech-to-text
│   ├── tts_service.py        # Dual TTS (Polly + Eleven Labs)
│   ├── openai_service.py     # GPT-4 conversation handling
│   └── customer_service.py   # Customer tier management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── test_services.py      # Service testing script
```

## 🔧 Environment Variables

```bash
# Telnyx
TELNYX_API_KEY=your_key_here
TELNYX_CONNECTION_ID=your_connection_id
TELNYX_WEBHOOK_URL=http://your-server:8000/webhooks/telnyx

# AI Services
DEEPGRAM_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here  # Optional

# AWS
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1
```

## 🧪 Testing

Run the test suite to verify all services:

```bash
python test_services.py
```

## 📈 Monitoring

The system logs all interactions and provides detailed error handling for production deployments.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions, please create a GitHub issue or contact the development team.

---

Built with ❤️ for Replk8.ai