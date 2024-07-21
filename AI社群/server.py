"""
server.py
Made by Daniel Huang
last update: 7/21/24
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from tfidf import create_user_profile

# Initialize the Flask application
app = Flask(__name__)

# Set up logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Base directory to save chat logs
# Using same BASE_DIR in tfdif.py, MANUALLY SYNC BOTH
BASE_DIR = "chat_logs"

# Conversation Function
# Save conversation between user and bot
# Save in local BASE_DIR
def save_conversation(user_id, user_message, bot_response):
    user_dir = os.path.join(BASE_DIR, str(user_id))  # Create a directory path for the user
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)  # Create the directory if it doesn't exist
    filename = os.path.join(user_dir, f"{user_id}.txt")  # Log file named after user_id
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Generate a timestamp for the log file
    with open(filename, 'a', encoding='utf-8') as file:  # Append to the log file
        # Write the conversation to the log file
        file.write(f"{timestamp} User: {user_message}\n")
        file.write(f"{timestamp} Bot: {bot_response}\n")

# Route to handle conversation logging
@app.route('/conversation', methods=['POST'])
def conversation():
    data = request.json  # Get JSON data from the request
    user_id = data['user_id']  # Extract user_id from the data
    user_message = data['user_message']  # Extract user_message from the data
    bot_response = data['bot_response']  # Extract bot_response from the data
    
    # Save the conversation to a log file
    save_conversation(user_id, user_message, bot_response)
    return jsonify({"status": "success"})  # Return a success response

# Route to fetch previous chat log
@app.route('/chatlog/<user_id>', methods=['GET'])
def fetch_chatlog(user_id):
    user_dir = os.path.join(BASE_DIR, str(user_id))  # Create a directory path for the user
    filename = os.path.join(user_dir, f"{user_id}.txt")  # Log file named after user_id
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            chat_log = file.read()  # Read the entire log file
        return jsonify({"status": "success", "chat_log": chat_log})
    else:
        return jsonify({"status": "success", "chat_log": ""})  # Return an empty response if no log exists

# Route to handle user exit and create persona
@app.route('/user_exit/<user_id>', methods=['POST'])
def user_exit(user_id):
    create_user_profile(user_id)
    return jsonify({"status": "success", "message": f"Profile created for user {user_id}."})

# Main entry point of the application
if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)  # Create the base directory if it doesn't exist
    app.run(debug=True)  # Run the Flask application in debug mode

