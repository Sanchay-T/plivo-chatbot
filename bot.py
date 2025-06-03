#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from fastapi import WebSocket
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.serializers.plivo import PlivoFrameSerializer
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.network.fastapi_websocket import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)
from config import get_config

load_dotenv()
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def run_bot(websocket_client: WebSocket, stream_id: str, call_id: Optional[str]):
    logger.info(f"🤖 STARTING AI BOT")
    logger.info(f"🆔 Stream ID: {stream_id}")
    logger.info(f"📞 Call ID: {call_id}")

    # Initialize Plivo serializer
    logger.info("🔧 Initializing Plivo serializer...")
    auth_id = os.getenv("PLIVO_AUTH_ID")
    auth_token = os.getenv("PLIVO_AUTH_TOKEN")
    logger.info(f"🔑 Using Plivo Auth ID: {auth_id}")

    serializer = PlivoFrameSerializer(
        stream_id=stream_id,
        call_id=call_id,
        auth_id=auth_id,
        auth_token=auth_token,
    )
    logger.info("✅ Plivo serializer created")

    # Initialize transport
    logger.info("🚀 Initializing WebSocket transport...")
    transport = FastAPIWebsocketTransport(
        websocket=websocket_client,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            vad_analyzer=SileroVADAnalyzer(),
            serializer=serializer,
        ),
    )
    logger.info("✅ WebSocket transport created")

    # Initialize AI services
    logger.info("🧠 Initializing OpenAI LLM...")
    openai_key = os.getenv("OPENAI_API_KEY")
    logger.info(f"🔑 OpenAI key: {'*' * (len(openai_key) - 4) + openai_key[-4:] if openai_key else 'NOT SET'}")
    llm = OpenAILLMService(api_key=openai_key)
    logger.info("✅ OpenAI LLM initialized")

    logger.info("🎤 Initializing Deepgram STT...")
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    logger.info(f"🔑 Deepgram key: {'*' * (len(deepgram_key) - 4) + deepgram_key[-4:] if deepgram_key else 'NOT SET'}")
    stt = DeepgramSTTService(api_key=deepgram_key)
    logger.info("✅ Deepgram STT initialized")

    logger.info("🗣️ Initializing Cartesia TTS...")
    cartesia_key = os.getenv("CARTESIA_API_KEY")
    config = get_config()
    voice_id = config.get_voice_id()
    logger.info(f"🔑 Cartesia key: {'*' * (len(cartesia_key) - 4) + cartesia_key[-4:] if cartesia_key else 'NOT SET'}")
    logger.info(f"🎵 Using voice ID: {voice_id}")
    tts = CartesiaTTSService(
        api_key=cartesia_key,
        voice_id=voice_id,
    )
    logger.info("✅ Cartesia TTS initialized with configured voice")

    # Set up conversation context
    logger.info("📚 Setting up AI conversation context...")
    system_prompt = config.get_system_prompt()
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]
    logger.info(f"📝 System message: {system_prompt}")

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)
    logger.info("✅ AI context and aggregator created")

    # Build the AI pipeline
    logger.info("🔧 Building AI processing pipeline...")
    pipeline = Pipeline(
        [
            transport.input(),  # Websocket input from client
            stt,  # Speech-To-Text (Deepgram)
            context_aggregator.user(),
            llm,  # LLM (OpenAI)
            tts,  # Text-To-Speech (Cartesia)
            transport.output(),  # Websocket output to client
            context_aggregator.assistant(),
        ]
    )
    logger.info("✅ AI pipeline built successfully")
    logger.info("🔄 Pipeline flow: Audio → STT → AI → TTS → Audio")

    # Create pipeline task
    logger.info("⚙️ Creating pipeline task...")
    audio_quality = config.get_audio_quality()
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=audio_quality,
            audio_out_sample_rate=audio_quality,
            allow_interruptions=True,
        ),
    )
    logger.info("✅ Pipeline task created with 8kHz audio and interruptions enabled")

    # Set up event handlers
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("🔗 CLIENT CONNECTED TO AI BOT!")
        logger.info("🎬 Starting conversation with introduction...")
        # Kick off the conversation.
        intro_message = {
            "role": "system", 
            "content": "Please introduce yourself to the caller as a friendly AI teacher from India. Say hello and ask how you can help them learn today."
        }
        messages.append(intro_message)
        logger.info(f"📤 Sending intro message: {intro_message['content']}")
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("📴 CLIENT DISCONNECTED FROM AI BOT")
        logger.info("🛑 Cancelling pipeline task...")
        await task.cancel()

    # Start the pipeline runner
    logger.info("🚀 Starting pipeline runner...")
    runner = PipelineRunner(handle_sigint=False, force_gc=True)
    
    logger.info("🎯 AI BOT IS READY! Waiting for audio...")
    logger.info("💫 The magic is about to begin...")

    await runner.run(task)
    
    logger.info("🏁 AI Bot session completed")
