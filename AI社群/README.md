# AI Community Chatbot Application

This application is designed to create an AI community for a company forum, where individual chatbots assist users and enable connections based on shared interests.

## Features

1. **Language Detection**: Detects the language of user input and responds in the same language.
2. **Conversation Storage**: Stores conversations in local files for continuity.
3. **Keyword Extraction**: Extracts and stores keywords from conversations to understand user preferences.
4. **User Profile Creation**: Creates detailed user profiles based on conversation analysis.

## Prerequisites

Ensure you have Python 3.7+ installed on your machine.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. (Optional) Download NLTK data (only if using NLTK):
    ```python
    python -m nltk.downloader stopwords
    ```

## Running the Application

1. Start the Flask server:
    ```bash
    python server.py
    ```

2. Start client side:
    ```bash
    python client.py
    ```

3. Interact with the chatbot through the configured client interface.

## Configuration

- **API Keys**: Ensure your API key for the MistralClient is saved in the specified location (`API_KEY_FILE`).

## Project Structure
.
├── server.py # Main server code
├── client.py # Client code
├── chatbot_module.py # Settings for chatbot AI
├── tfidf.py # TF-IDF computation and profile analysis
├── requirements.txt # Required Python packages
├── README.md # This file
└── <other_files> # Other necessary files and directories

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## License

This project is licensed under the MIT License.
