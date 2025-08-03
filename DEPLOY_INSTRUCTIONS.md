# Deploy AI Voice Agent to EC2

## Method 1: Quick Copy-Paste (Recommended)

1. **SSH into your EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@3.136.7.249
   ```

2. **Create project directory:**
   ```bash
   mkdir -p ~/replk8-voice-agent
   cd ~/replk8-voice-agent
   ```

3. **Install Python and dependencies:**
   ```bash
   sudo yum update -y
   sudo yum install -y python3 python3-pip
   ```

4. **Create the files** (copy-paste each file contents):

   **Create requirements.txt:**
   ```bash
   cat > requirements.txt << 'EOF'
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   requests==2.31.0
   pydantic==2.5.0
   python-multipart==0.0.6
   aiofiles==23.2.1
   httpx==0.25.2
   deepgram-sdk==3.2.7
   openai==1.3.7
   boto3==1.34.0
   botocore==1.34.0
   telnyx==2.0.0
   python-dotenv==1.0.0
   EOF
   ```

   **Create .env file:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual API keys
   ```
   
   **Or create manually:**
   ```bash
   cat > .env << 'EOF'
   # Telnyx Configuration
   TELNYX_API_KEY=your_telnyx_api_key_here
   TELNYX_CONNECTION_ID=your_telnyx_connection_id_here
   TELNYX_WEBHOOK_URL=http://your-server-ip:8000/webhooks/telnyx

   # AI Services
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here

   # AWS Configuration (for Polly)
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
   AWS_REGION=us-east-1
   POLLY_VOICE=Joanna

   # Application Settings
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   EOF
   ```

5. **Create directory structure:**
   ```bash
   mkdir -p src/services
   ```

6. **Install dependencies:**
   ```bash
   pip3 install --user -r requirements.txt
   ```

7. **Open port 8000 in your Security Group:**
   - Go to EC2 Console > Security Groups
   - Find your instance's security group
   - Add Inbound Rule: Custom TCP, Port 8000, Source: 0.0.0.0/0

8. **Start the server:**
   ```bash
   python3 src/app.py
   ```

## Method 2: Use Git (if you have a GitHub repo)

1. Push code to GitHub
2. Clone on EC2:
   ```bash
   git clone your-repo-url
   cd your-repo
   pip3 install --user -r requirements.txt
   python3 src/app.py
   ```

## Method 3: SCP Upload (if you have SSH key)

```bash
scp -i your-key.pem -r ./replk8-voice-agent ec2-user@3.136.7.249:~/
```

---

## After deployment, test with:
```bash
curl http://3.136.7.249:8000
```

Should return: `{"message":"Replk8 AI Voice Agent is running"}`