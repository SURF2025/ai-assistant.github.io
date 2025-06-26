# Streamlit Llama Chat Application

This project is a chat application built using Streamlit and the Llama 3.1 model. It allows users to interact with the model in a conversational manner.

## Project Structure

```
streamlit-llama-chat-app
├── src
│   ├── app.py          # Main entry point for the Streamlit application
│   ├── llama_client.py  # Manages connection to the Llama 3.1 model
│   └── utils.py        # Utility functions for the application
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-llama-chat-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have the Llama 3.1 model set up and accessible via Ollama.

## Usage

To run the application, execute the following command:
```
streamlit run src/app.py
```

Open your web browser and navigate to `http://localhost:8501` to start chatting with the Llama 3.1 model.

## Features

- Interactive chat interface
- Real-time responses from the Llama 3.1 model
- User-friendly design for seamless conversation flow

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.