# Plivo Outbound AI Chatbot

This project is a FastAPI-based AI chatbot that integrates with Plivo to make **outbound calls** and provide real-time AI conversations. The chatbot acts as an elementary teacher and can call any phone number you specify through a web interface.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)

## Features

- **🤖 Outbound AI Calling**: Input any phone number and the AI chatbot will call them
- **🎓 AI Teacher**: Acts as an elementary teacher with natural conversation
- **🌐 Web Interface**: Simple web form to initiate calls
- **🎵 Real-time Audio**: Live voice conversation using WebSocket streaming
- **⚡ FastAPI**: Modern, fast web framework with automatic API docs
- **🔄 WebSocket Support**: Real-time bidirectional audio communication
- **🐳 Dockerized**: Easy deployment using Docker

## Requirements

- Python 3.10+
- Plivo Account with voice-enabled phone number
- Docker (for containerized deployment)
- ngrok (for tunneling)
- API Keys for:
  - OpenAI (for LLM)
  - Deepgram (for Speech-to-Text)
  - Cartesia (for Text-to-Speech)

## Installation

1. **Clone and setup**:
   ```sh
   git clone <repository-url>
   cd plivo-chatbot
   ```

2. **Set up a virtual environment** (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Create .env file**:
   ```sh
   cp env.example .env
   ```
   Then edit `.env` with your actual credentials.

## Configuration

### 1. Environment Variables

Update your `.env` file with the following credentials:

```env
# Plivo credentials (from your Plivo console)
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token

# AI service API keys
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
CARTESIA_API_KEY=your_cartesia_api_key

# Server URL (your ngrok URL without https://)
SERVER_URL=abc123.ngrok.io
```

### 2. Setup ngrok for tunneling

1. **Install ngrok**: Follow instructions on [ngrok website](https://ngrok.com/download)

2. **Start ngrok** (in a separate terminal):
   ```sh
   ngrok http 8765
   ```

3. **Update .env**: Copy your ngrok URL (without `https://`) to `SERVER_URL` in `.env`
   ```
   SERVER_URL=abc123.ngrok.io
   ```

### 3. Configure streams.xml

Update `templates/streams.xml` with your ngrok URL:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">wss://abc123.ngrok.io/ws</Stream>
</Response>
```

### 4. Get Required API Keys

- **Plivo**: Get Auth ID and Token from [Plivo Console](https://console.plivo.com/)
- **OpenAI**: Get API key from [OpenAI Platform](https://platform.openai.com/)
- **Deepgram**: Get API key from [Deepgram Console](https://console.deepgram.com/)
- **Cartesia**: Get API key from [Cartesia](https://cartesia.ai/)

## Running the Application

### Option 1: Using Python

```sh
# Make sure you're in the project directory and virtual environment is activated
python server.py
```

### Option 2: Using Docker

1. **Build the Docker image**:
   ```sh
   docker build -t plivo-outbound-chatbot .
   ```

2. **Run the Docker container**:
   ```sh
   docker run -it --rm -p 8765:8765 --env-file .env plivo-outbound-chatbot
   ```

The server will start on `http://localhost:8765`

## Usage

### Making Outbound Calls

1. **Open the web interface**: Go to `http://localhost:8765` in your browser

2. **Fill out the form**:
   - **Phone Number**: Enter the target number with country code (e.g., `+1234567890`)
   - **Caller ID**: Enter your Plivo phone number (the number making the call)

3. **Click "Start Call"**: The AI chatbot will immediately call the target number

4. **Conversation begins**: When the person answers, they'll be connected to the AI teacher who will introduce themselves and start a conversation

### How It Works

```
📱 You → 🌐 Web Interface → 🚀 Plivo API → 📞 Target Phone
                                                    ↓
🤖 AI Teacher ← 🎧 Audio Stream ← 📡 WebSocket ← 📞 When Answered
```

1. **Web Form**: You enter a phone number via the web interface
2. **Plivo API Call**: Server uses Plivo API to initiate outbound call
3. **Call Answered**: When target answers, Plivo hits the `/answer` endpoint
4. **Stream Started**: Server returns XML to start audio streaming
5. **AI Conversation**: Audio flows through WebSocket to the AI pipeline:
   - **Speech → Text** (Deepgram)
   - **AI Processing** (OpenAI as elementary teacher)
   - **Text → Speech** (Cartesia)
   - **Audio back to caller**

### API Endpoints

- `GET /` - Web interface for making calls
- `POST /make-call` - Initiate outbound call
- `POST /answer` - Plivo callback when call is answered
- `POST /hangup` - Plivo callback when call ends
- `WebSocket /ws` - Real-time audio streaming

## Customizing the AI

You can modify the AI personality in `bot.py`:

```python
messages = [
    {
        "role": "system",
        "content": "You are an elementary teacher in an audio call. Your output will be converted to audio so don't include special characters in your answers. Respond to what the student said in a short short sentence.",
    },
]
```

Change this to make the AI act as:
- Customer support agent
- Sales representative  
- Personal assistant
- Any character you want!

## Troubleshooting

### Common Issues

1. **Call fails**: Check Plivo credentials and phone number format
2. **No audio**: Verify ngrok URL in `streams.xml` and `.env`
3. **AI not responding**: Check OpenAI/Deepgram/Cartesia API keys
4. **WebSocket errors**: Ensure ngrok is running and URL is correct

### Logs

The application provides detailed logs. Watch for:
- "Call initiated successfully" - Outbound call started
- "Outbound call answered" - Target picked up
- "WebSocket connection accepted" - Audio streaming started

## Key Differences from Twilio

- Plivo uses `streamId` instead of `streamSid`
- Plivo uses `callId` instead of `callSid`
- Plivo uses `<Stream>` element instead of `<Connect><Stream>`
- Plivo's Stream element has `bidirectional`, `keepCallAlive`, and `contentType` attributes
- Plivo API authentication uses Auth ID and Auth Token

## Next Steps

- Deploy to cloud (AWS, GCP, Azure) instead of using ngrok
- Add call recording and transcription
- Implement call analytics and reporting
- Add multiple AI personalities
- Integrate with CRM systems
- Add SMS capabilities
