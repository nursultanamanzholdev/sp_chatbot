# Project Setup Guide

This README provides complete instructions for setting up and launching the project, including both backend and frontend components.

## Prerequisites

- Node.js v20.11.1
- Python 3.10+

## Project Setup

### Backend Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   
   **Windows:**
   ```bash
   .\venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python migrations.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

## Running the Project

### Start the Backend

1. With the virtual environment activated, run:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   This will start the backend server on http://localhost:8000

### Start the Frontend

1. Open a new terminal window
2. Activate the virtual environment (if not already activated)
3. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
4. Run the development server:
   ```bash
   npm run dev
   ```
   This will start the frontend development server

## Accessing the Application

After starting both the backend and frontend servers, you can access the application by opening your browser and navigating to the URL displayed in the frontend terminal (typically http://localhost:3000 or http://localhost:5173).

## Stopping the Servers

To stop either server, press `Ctrl+C` in the respective terminal window.

## Troubleshooting

- If you encounter dependency issues with the frontend, try running `npm install --force` instead of `npm install --legacy-peer-deps`
- Ensure that both backend and frontend servers are running simultaneously
- Check console output for any error messages
