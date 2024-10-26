import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Telegram bot token
TELEGRAM_BOT_TOKEN = ""
# Base URL for Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Define the data model for incoming messages
class TelegramMessage(BaseModel):
    update_id: int
    message: dict
    


@app.post("/receive-message/")
async def receive_message(update: TelegramMessage):
    logger.info("Received message from Telegram: %s", update.dict())
    # Check if the message contains necessary fields
    if "chat" not in update.message or "text" not in update.message:
        logger.error("Update does not contain 'chat' or 'text' fields: %s", update.message)
        print(TelegramMessage.message)
        raise HTTPException(status_code=400, detail="Invalid message format")

    chat_id = update.message["chat"]["id"]
    text = update.message["text"]

    logger.info("Chat ID: %s, Text: %s", chat_id, text)

    model_response = call_your_model(text)
    
    response_status = send_to_telegram(chat_id, "server response")
    
    if not response_status:
        logger.error("Failed to send message to Telegram.")
        raise HTTPException(status_code=500, detail="Failed to send message to Telegram")

    logger.info("Sent response to Telegram: %s", model_response)
    return {"status": "success"}

def call_your_model(prompt: str):
    return f"Processed your request: {prompt}"

def send_to_telegram(chat_id: int, message: str):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() 
        logger.info("Response from Telegram API: %s", response.json())
        return True
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error occurred: %s", http_err)
        return False
    except Exception as err:
        logger.error("An error occurred: %s", err)
        return False
