import asyncio
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
import os
from dotenv import load_dotenv , find_dotenv
from tools import get_crypto_price
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv(find_dotenv())

gemini_api_key = os.getenv("GOOGLE_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

run_config = RunConfig(
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    model_provider=client,
    tracing_disabled=True
)
CryptoDataAgent = Agent(
    name="CryptoDataAgent",
    instructions="You are a helpful agent that gives live cryptocurrency prices using Binance API.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[get_crypto_price]
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Welcome to the Gemini-powered chatbot! How can I assist you today?").send()
    

@cl.on_message
async def handle_message(message:cl.Message):
    history=cl.user_session.get("history")
    msg=cl.Message(content="")
    await msg.send()
    history.append({"role":"user","content":message.content})
    result = Runner.run_streamed(CryptoDataAgent, input=history, run_config=run_config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("history",history)
    # await cl.Message(content=result.final_output).send()
