# SLA Chatbot

Second Language Acquisition (SLA) chatbot platform designed to help children learn through interactive conversations.
The web application is available on: https://chatbot-frontend-oeip.onrender.com

## Features

- **User Authentication**: Secure login and registration system
- **PDF Processing**: Upload PDF books that are automatically converted into interactive dialog format
- **Custom Prompts**: Create and manage custom conversation prompts
- **Educational Mode**: Interactive learning sessions based on textbook content
- **Language Learning**: English language tutoring with adaptive feedback
- **Conversation History**: Track and review past conversations
- **Notes System**: Save and organize notes with feedback

## Technical Stack

### Backend
- FastAPI framework with SQLAlchemy ORM
- PostgreSQL database
- PDF processing pipeline

### Frontend
- Next.js React framework
- Tailwind CSS for styling
- Responsive design for all devices

## Raspberry Pi script

The repository includes `chatbot_raspberry.py` that provides functionality for running the chatbot on a Raspberry PI 5 device. This script includes:

- TTS and ASR capabilites
- Language model that generates text based on json dialogs
- Support for chat and lecture learning modes
- Audio recording and text-to-speech conversion

## Modes of Operation

1. **Chat Mode**: General purpose conversations
2. **Lecture Mode**: Helps children understand concepts from textbooks

