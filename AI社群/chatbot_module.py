import logging
import sys
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from pyreadline3 import Readline

readline = Readline()  # For readline can't work on windows bug fixed

# List of available models
MODEL_LIST = [
    "mistral-small-latest",
    "mistral-medium-latest",
    "mistral-large-latest", 
    "codestral-latest",
]

# Default values for model and temperature
DEFAULT_MODEL = "mistral-small-latest"
DEFAULT_TEMPERATURE = 0.7  # Random 0-1

# A dictionary of all commands and their arguments, used for tab completion.
COMMAND_LIST = {
    "/new": {},
    "/help": {},
    "/model": {model: {} for model in MODEL_LIST},  # Nested completions for models
    "/system": {},
    "/temperature": {},
    "/config": {},
    "/quit": {},
    "/exit": {},
}

# Logging
# Only save log to file when error happens

# Logging configuration with file and console handlers
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logger = logging.getLogger("chatbot")
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler("chatbot.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Add handlers to the logger
logger.addHandler(file_handler)


# Input Function
# Completing user inputs
# Find command completions based on the current input
def find_completions(command_dict, parts):
    if not parts:
        return command_dict.keys()
    if parts[0] in command_dict:
        return find_completions(command_dict[parts[0]], parts[1:])
    else:
        return [cmd for cmd in command_dict if cmd.startswith(parts[0])]

# Completer function for readline
def completer(text, state):
    buffer = readline.get_line_buffer()
    line_parts = buffer.lstrip().split(" ")
    options = find_completions(COMMAND_LIST, line_parts[:-1])

    try:
        return [option for option in options if option.startswith(line_parts[-1])][state]
    except IndexError:
        return None

readline.set_completer(completer)
readline.set_completer_delims(" ")
# Enable tab completion
readline.parse_and_bind("tab: complete")

# ChatBot class definition
class ChatBot:
    def __init__(self, api_key, model, system_message=None, temperature=DEFAULT_TEMPERATURE):
        if not api_key:
            raise ValueError("An API key must be provided to use the Mistral API.")
        self.client = MistralClient(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.system_message = system_message

    # Display the opening instructions
    def opening_instructions(self):
        print(
            """
To chat: type your message and hit enter
To start a new chat: /new
To switch model: /model <model name>
To switch system message: /system <message>
To switch temperature: /temperature <temperature>
To see current config: /config
To exit: /exit, /quit, or hit CTRL+C
To see this help: /help
"""
        )

    # Start a new chat session
    def new_chat(self):
        print("")
        print(f"Starting new chat with model: {self.model}, temperature: {self.temperature}")
        print("")
        self.messages = []
        if self.system_message:
            self.messages.append(ChatMessage(role="system", content=self.system_message))

    # Switch the current model
    def switch_model(self, input):
        model = self.get_arguments(input)
        if model in MODEL_LIST:
            self.model = model
            logger.info(f"Switching model: {model}")
        else:
            logger.error(f"Invalid model name: {model}")

    # Switch the system message
    def switch_system_message(self, input):
        system_message = self.get_arguments(input)
        if system_message:
            self.system_message = system_message
            logger.info(f"Switching system message: {system_message}")
            self.new_chat()
        else:
            logger.error(f"Invalid system message: {system_message}")

    # Switch the temperature
    def switch_temperature(self, input):
        temperature = self.get_arguments(input)
        try:
            temperature = float(temperature)
            if temperature < 0 or temperature > 1:
                raise ValueError
            self.temperature = temperature
            logger.info(f"Switching temperature: {temperature}")
        except ValueError:
            logger.error(f"Invalid temperature: {temperature}")

    # Show the current configuration
    def show_config(self):
        print("")
        print(f"Current model: {self.model}")
        print(f"Current temperature: {self.temperature}")
        print(f"Current system message: {self.system_message}")
        print("")

    # Collect user input
    def collect_user_input(self):
        print("")
        return input("YOU: ")

    # Run inference using the Mistral API
    def run_inference(self, content):
        print("")
        print("MISTRAL:")
        print("")

        self.messages.append(ChatMessage(role="user", content=content))

        chatbot_response = ""
        logger.debug(f"Running inference with model: {self.model}, temperature: {self.temperature}")
        logger.debug(f"Sending messages: {self.messages}")
        for chunk in self.client.chat_stream(model=self.model, temperature=self.temperature, messages=self.messages):
            response = chunk.choices[0].delta.content
            if response is not None:
                print(response, end="", flush=True)
                chatbot_response += response

        print("", flush=True)

        if chatbot_response:
            self.messages.append(ChatMessage(role="assistant", content=chatbot_response))
        logger.debug(f"Current messages: {self.messages}")
        return chatbot_response

    # Get the command from the user input
    def get_command(self, input):
        return input.split()[0].strip()

    # Get the arguments from the user input
    def get_arguments(self, input):
        try:
            return " ".join(input.split()[1:])
        except IndexError:
            return ""

    # Check if the input is a command
    def is_command(self, input):
        return self.get_command(input) in COMMAND_LIST

    # Execute the command based on the user input
    def execute_command(self, input):
        command = self.get_command(input)
        if command in ["/exit", "/quit"]:
            self.exit()
        elif command == "/help":
            self.opening_instructions()
        elif command == "/new":
            self.new_chat()
        elif command == "/model":
            self.switch_model(input)
        elif command == "/system":
            self.switch_system_message(input)
        elif command == "/temperature":
            self.switch_temperature(input)
        elif command == "/config":
            self.show_config()

    # Start the chatbot
    def start(self):
        self.opening_instructions()
        self.new_chat()

    # Exit the chatbot
    def exit(self):
        logger.debug("Exiting chatbot")
        sys.exit(0)
