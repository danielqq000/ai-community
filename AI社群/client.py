import argparse
import logging
import requests
import sys
from chatbot_module import *


# API Function
# Read the API key from file
def read_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise ValueError(f"API key file not found: {file_path}")

# To-Server Function
# Send conversation data to the server
def send_conversation_to_server(user_id, user_message, bot_response):
    data = {
        "user_id": user_id,
        "user_message": user_message,
        "bot_response": bot_response
    }
    response = requests.post("http://localhost:5000/conversation", json=data)
    if response.status_code != 200:
        logger.error(f"Failed to save conversation: {response.text}")

# Main Function
# Parse arguments and start the chatbot
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple chatbot using the Mistral API")
    parser.add_argument(
        "--api-key-file",
        default="api_key.txt",
        help="Path to the file containing the Mistral API key. Defaults to api_key.txt",
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest", "codestral-latest"],
        default=DEFAULT_MODEL,
        help="Model for chat inference. Choices are %(choices)s. Defaults to %(default)s",
    )
    parser.add_argument("-s", "--system-message", help="Optional system message to prepend.")
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help="Optional temperature for chat inference. Defaults to %(default)s",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging based on the debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug(
        f"Starting chatbot with model: {args.model}, "
        f"temperature: {args.temperature}, "
        f"system message: {args.system_message}"
    )

    # Starting chatbot
    try:
        api_key = read_api_key(args.api_key_file)  # Read the API key from the file
        bot = ChatBot(api_key, args.model, args.system_message, args.temperature)  # Initialize the ChatBot
        user_id = input("Please enter your user ID: ")
        bot.start()

        while True:
            try:
                user_message = bot.collect_user_input()
                if bot.is_command(user_message):
                    bot_response = bot.execute_command(user_message)
                else:
                    bot_response = bot.run_inference(user_message)
            except KeyboardInterrupt:
                bot.exit()

            # Send conversation to server
            send_conversation_to_server(user_id, user_message, bot_response)    

    except Exception as e:
        logger.error(e)
        sys.exit(1)
