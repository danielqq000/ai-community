"""
tfidf.py
Made by Daniel Huang
Last update: 7/21/24
"""

import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from mistralai.client import MistralClient  # Import MistralAI API client
from mistralai.models.chat_completion import ChatMessage
from client import read_api_key  # Lazy 

# Using same BASE_DIR in server.py, MANUALLY SYNC BOTH
BASE_DIR = "chat_logs"

def read_chat_log(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def preprocess_text(text):
    # Remove non-alphanumeric characters
    text = re.sub(r'\W+', ' ', text)
    return text.lower()

# Compute tfidf scores from given chat log
# Pre-done function
def compute_tfidf(chat_log):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([chat_log])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
    return tfidf_scores

def read_tfidf_scores(file_path):
    tfidf_scores = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            word, score = line.strip().split(': ')
            tfidf_scores[word] = float(score)
    return tfidf_scores

def update_tfidf_scores(existing_scores, new_scores):
    update_scores = existing_scores.copy()
    for word, score in new_scores.items():
        if word in update_scores:
            update_scores[word] += score  # Update if exist
        else:
            update_scores[word] = score  # Make if not exist
    return update_scores

def write_tfidf_output(file_path, tfidf_scores):
    with open(file_path, 'w', encoding='utf-8') as file:
        for word, score in tfidf_scores.items():
            file.write(f"{word}: {score}\n")

# Computing Funciton
# Computes tfidf score from given user directory, using user's chat log
def compute_score(dir_path, user_id):
    # Check if file exist, which should be
    chat_log_path = os.path.join(dir_path, f"{user_id}.txt")
    if not os.path.exists(chat_log_path):
        print(f"Chat log for user {user_id} does not exist.")
        exit(1)

    # Read and preprocess
    chat_log = preprocess_text(read_chat_log(chat_log_path))
    tfidf_scores = compute_tfidf(chat_log)
    return tfidf_scores

# Updating Function
# Update new scores to old one, merge both together
def score_update(dir_path, new_scores, user_id):
    score_path = os.path.join(dir_path, f"{user_id}_tfidf.txt")
    # If old scores exist, read and merge
    if os.path.exists(score_path):
        old_scores = read_tfidf_scores(score_path)
        new_scores = update_tfidf_scores(old_scores, new_scores)

    write_tfidf_output(score_path, new_scores)
    return new_scores

# Profiling Function
# Based on tfidf scores, ask MistralAI about this user's profile
def profile_analysis(dir_path, user_scores, user_id):
    api_key = read_api_key("api_key2.txt")
    client = MistralClient(api_key=api_key)

    analysis_prompt = """
    You will be given a TF-IDF scores from a conversation between a user and a AI chatbot.
    Analyze the following TF-IDF scores and create a user profile based on these keywords:
    """
    for word, score in user_scores.items():
        analysis_prompt += f"{word}: {score}\n"
    analysis_prompt += "\nCreate a detailed user profile:"

    messages = [ChatMessage(role="user", content=analysis_prompt)]
    response = client.chat(model="mistral-large-latest", temperature=0.7, messages=messages)

    profile_content = response.choices[0].message.content

    profile_path = os.path.join(BASE_DIR, str(user_id), f"{user_id}_profile.txt")
    with open(profile_path, 'w', encoding='utf-8') as file:
        file.write(profile_content)

# File main funciton
# Parameter: user ID
# Funciton:
# find user's directory, read chat log and analysis, create tfidf scores
# read old scores if exists, and update new scores in new file user_id_tfidf.txt
def create_user_profile(user_id):
    user_dir = os.path.join(BASE_DIR, str(user_id))
    if not os.path.exists(user_dir):
        print(f"Directory for user {user_id} does not exist.")
        exit(1)

    print(f"Computing user {user_id} tfidf scores...     ", end='')
    tfidf_scores = compute_score(user_dir, user_id)
    print("Done.")
    print(f"Updating user {user_id} tfidf scores...      ", end='')
    user_scores = score_update(user_dir, tfidf_scores, user_id)
    print("Done.")
    print(f"Creating user {user_id} profile...      ", end='')
    profile_analysis(user_dir, user_scores, user_id)
    print("Done.")

