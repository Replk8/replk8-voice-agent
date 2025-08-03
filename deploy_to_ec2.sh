#!/bin/bash
# Deploy Replk8 AI Voice Agent to EC2

EC2_HOST="3.136.7.249"
EC2_USER="ec2-user"  # Change if different (ubuntu for Ubuntu instances)
KEY_PATH="path/to/your/key.pem"  # Update with your actual key path

echo "Deploying AI Voice Agent to EC2..."

# Create project directory on EC2
ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "mkdir -p ~/replk8-voice-agent"

# Copy all files to EC2
scp -i $KEY_PATH -r ./* $EC2_USER@$EC2_HOST:~/replk8-voice-agent/

echo "Files copied to EC2. Now connecting to install dependencies..."

# SSH into EC2 and set up the environment
ssh -i $KEY_PATH $EC2_USER@$EC2_HOST << 'EOF'
cd ~/replk8-voice-agent

# Install Python 3 and pip if not already installed
sudo yum update -y
sudo yum install -y python3 python3-pip

# Install Python dependencies
pip3 install --user -r requirements.txt

# Make sure port 8000 is open in security group
echo "Make sure port 8000 is open in your EC2 security group!"

# Start the server
echo "Starting AI Voice Agent server..."
python3 src/app.py
EOF