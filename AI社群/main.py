import argparse
import logging
import sys
from chatbot_module import *

def read_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise ValueError(f"API key file not found: {file_path}")

# Main function to parse arguments and start the chatbot
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

    try:
        api_key = read_api_key(args.api_key_file)
        bot = ChatBot(api_key, args.model, args.system_message, args.temperature)
        bot.start()
    except Exception as e:
        logger.error(e)
        sys.exit(1)
