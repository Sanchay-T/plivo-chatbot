#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import argparse
import json
import os

import uvicorn
import plivo
from bot import run_bot
from fastapi import FastAPI, WebSocket, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from starlette.responses import HTMLResponse
from dotenv import load_dotenv
from config import get_config, CARTESIA_VOICES, PROMPT_TEMPLATES

load_dotenv()

# Configure detailed logging
logger.remove()
logger.add("chatbot.log", rotation="1 MB", level="DEBUG")
logger.add(lambda msg: print(f"🔍 {msg}", end=""), level="DEBUG")

logger.info("🚀 Starting Plivo Outbound AI Chatbot")

# Auto-update streams.xml with server URL
def update_streams_xml():
    """Update streams.xml with the SERVER_URL from .env"""
    server_url = os.getenv("SERVER_URL")
    if not server_url:
        logger.warning("⚠️ SERVER_URL not set in .env - streams.xml may need manual update")
        return False
    
    template_path = "templates/streams.xml.template"
    output_path = "templates/streams.xml"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        updated_content = content.replace('<your server url>', server_url)
        
        with open(output_path, 'w') as f:
            f.write(updated_content)
        
        logger.info(f"✅ Updated streams.xml with WebSocket URL: wss://{server_url}/ws")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update streams.xml: {e}")
        return False

# Update streams.xml on startup
update_streams_xml()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Plivo client for outbound calls
plivo_auth_id = os.getenv("PLIVO_AUTH_ID")
plivo_auth_token = os.getenv("PLIVO_AUTH_TOKEN")

logger.info(f"🔑 Plivo Auth ID: {plivo_auth_id}")
logger.info(f"🔑 Plivo Auth Token: {'*' * (len(plivo_auth_token) - 4) + plivo_auth_token[-4:] if plivo_auth_token else 'NOT SET'}")

plivo_client = plivo.RestClient(
    auth_id=plivo_auth_id,
    auth_token=plivo_auth_token
)

logger.info("✅ Plivo client initialized")

@app.get("/")
async def home(request: Request):
    """Modern web interface to initiate outbound calls"""
    logger.info("📱 Loading modern web interface")
    config = get_config()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "default_caller_id": config.get_caller_id(),
        "default_target_number": config.get_target_number()
    })

@app.post("/make-call")
async def make_outbound_call(request: Request, phone: str = Form(...), caller_id: str = Form(...)):
    """Initiate an outbound call using Plivo API"""
    logger.info("🚀 STARTING OUTBOUND CALL")
    logger.info(f"📞 Target Number: {phone}")
    logger.info(f"🆔 Caller ID: {caller_id}")
    
    try:
        # Get the server URL
        server_url = os.getenv("SERVER_URL", "your-ngrok-url.ngrok.io")
        logger.info(f"🌐 Server URL: {server_url}")
        
        answer_url = f"https://{server_url}/answer"
        hangup_url = f"https://{server_url}/hangup"
        
        logger.info(f"🔗 Answer URL: {answer_url}")
        logger.info(f"🔗 Hangup URL: {hangup_url}")
        
        # Make the outbound call
        logger.info("📡 Making Plivo API call...")
        response = plivo_client.calls.create(
            from_=caller_id,
            to_=phone,
            answer_url=answer_url,
            answer_method='POST',
            hangup_url=hangup_url,
            hangup_method='POST'
        )
        
        logger.info("✅ CALL INITIATED SUCCESSFULLY!")
        
        # Log the full response to see its structure
        logger.info(f"📊 API Response type: {type(response)}")
        logger.info(f"📊 API Response dir: {dir(response)}")
        logger.info(f"📊 API Response: {response}")
        
        # Try to get call UUID - different ways Plivo might return it
        call_uuid = None
        if hasattr(response, 'call_uuid'):
            call_uuid = response.call_uuid
        elif hasattr(response, 'request_uuid'):
            call_uuid = response.request_uuid
        elif hasattr(response, 'uuid'):
            call_uuid = response.uuid
        elif hasattr(response, 'message_uuid'):
            call_uuid = response.message_uuid
        else:
            call_uuid = "Generated successfully"
            
        logger.info(f"🆔 Call UUID: {call_uuid}")
        
        return templates.TemplateResponse("call_success.html", {
            "request": request,
            "phone": phone,
            "caller_id": caller_id,
            "call_uuid": call_uuid
        })
        
    except Exception as e:
        logger.error(f"❌ CALL FAILED: {str(e)}")
        logger.error(f"📊 Exception details: {type(e).__name__}")
        
        return templates.TemplateResponse("call_error.html", {
            "request": request,
            "phone": phone,
            "caller_id": caller_id,
            "error": str(e)
        })

@app.post("/answer")
async def answer_call():
    """Handle when outbound call is answered - return XML to start streaming"""
    logger.info("📞 OUTBOUND CALL ANSWERED!")
    logger.info("🎵 Returning stream XML to start audio streaming")
    
    try:
        xml_content = open("templates/streams.xml").read()
        logger.info(f"📋 Stream XML content: {xml_content}")
        return HTMLResponse(content=xml_content, media_type="application/xml")
    except Exception as e:
        logger.error(f"❌ Failed to read streams.xml: {e}")
        # Fallback XML
        fallback_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">wss://your-ngrok-url.ngrok.io/ws</Stream>
</Response>"""
        return HTMLResponse(content=fallback_xml, media_type="application/xml")

@app.post("/hangup")
async def hangup_call():
    """Handle call hangup events"""
    logger.info("📴 CALL ENDED - Hangup received")
    return HTMLResponse(content="<Response></Response>", media_type="application/xml")

# API Endpoints for Configuration
@app.get("/api/settings")
async def get_settings():
    """Get current configuration settings"""
    config = get_config()
    return JSONResponse({
        "ai": {
            "system_prompt": config.get_system_prompt(),
            "voice_id": config.get_voice_id(),
            "audio_quality": config.get_audio_quality()
        },
        "call": {
            "default_caller_id": config.get_caller_id(),
            "default_target_number": config.get_target_number()
        }
    })

@app.post("/api/settings")
async def update_settings(request: Request):
    """Update configuration settings"""
    try:
        data = await request.json()
        config = get_config()
        
        # Update AI settings
        ai_updates = {}
        if "system_prompt" in data:
            ai_updates["system_prompt"] = data["system_prompt"]
        if "voice_id" in data:
            ai_updates["voice_id"] = data["voice_id"]
        if "audio_quality" in data:
            ai_updates["audio_quality"] = int(data["audio_quality"])
        
        if ai_updates:
            config.update_ai_config(**ai_updates)
        
        # Update call settings
        call_updates = {}
        if "default_caller_id" in data:
            call_updates["default_caller_id"] = data["default_caller_id"]
        if "default_target_number" in data:
            call_updates["default_target_number"] = data["default_target_number"]
        
        if call_updates:
            config.update_call_config(**call_updates)
        
        logger.info("✅ Configuration updated successfully")
        return JSONResponse({"status": "success", "message": "Settings updated successfully"})
        
    except Exception as e:
        logger.error(f"❌ Failed to update settings: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)

@app.get("/api/voices")
async def get_voices():
    """Get available voice options"""
    return JSONResponse({
        "voices": [
            {"id": voice_id, "name": name}
            for voice_id, name in CARTESIA_VOICES.items()
        ]
    })

@app.get("/api/prompts")
async def get_prompt_templates():
    """Get available prompt templates"""
    return JSONResponse({
        "templates": [
            {"id": template_id, "name": template_id.title(), "content": content}
            for template_id, content in PROMPT_TEMPLATES.items()
        ]
    })

@app.get("/api/call-history")
async def get_call_history():
    """Get call history (placeholder for future implementation)"""
    # This would integrate with a database or log file
    return JSONResponse({
        "calls": [],
        "total": 0,
        "successful": 0,
        "failed": 0
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("🔌 NEW WEBSOCKET CONNECTION ATTEMPT")
    await websocket.accept()
    logger.info("✅ WebSocket connection accepted")

    try:
        # Plivo sends a start event when the stream begins
        logger.info("⏳ Waiting for start message from Plivo...")
        start_data = websocket.iter_text()
        start_message = json.loads(await start_data.__anext__())

        logger.info("📨 RECEIVED START MESSAGE:")
        logger.info(f"📊 Full message: {json.dumps(start_message, indent=2)}")

        # Extract stream_id and call_id from the start event
        start_info = start_message.get("start", {})
        stream_id = start_info.get("streamId")
        call_id = start_info.get("callId")

        logger.info(f"🆔 Stream ID: {stream_id}")
        logger.info(f"📞 Call ID: {call_id}")

        if not stream_id:
            logger.error("❌ NO STREAM ID FOUND IN START MESSAGE!")
            await websocket.close()
            return

        logger.info("🤖 STARTING AI BOT...")
        await run_bot(websocket, stream_id, call_id)
        
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        logger.error(f"📊 Exception type: {type(e).__name__}")
        await websocket.close()


if __name__ == "__main__":
    config = get_config()
    logger.info("🌟 Starting FastAPI server on port 8765")
    logger.info(f"🔗 Web interface will be available at: http://localhost:8765")
    logger.info(f"📞 Default configuration:")
    logger.info(f"   🆔 Caller ID: {config.get_caller_id()}")
    logger.info(f"   📱 Target: {config.get_target_number()}")
    logger.info(f"   🎵 Voice: {config.get_voice_id()}")
    logger.info(f"   🧠 System prompt: {config.get_system_prompt()[:50]}...")
    
    uvicorn.run(app, host="0.0.0.0", port=8765)
