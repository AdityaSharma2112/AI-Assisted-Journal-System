# Arvyax Journaling App

A full-stack AI-powered journaling application that allows users to record their thoughts, track the ambience of their environment, and receive real-time emotional insights using the Gemini LLM.

## Tech Stack
* **Frontend:** React, Vite, Tailwind CSS, Axios
* [cite_start]**Backend:** FastAPI, Python 3.11 [cite: 1]
* **Database:** MongoDB (using PyMongo)
* **AI Integration:** Gemini 2.5 Flash (via OpenAI SDK compatibility)
* **Caching & Rate Limiting:** Upstash Redis, SlowAPI
* **Containerization:** Docker & Docker Compose

## Features
* **Create Entries:** Save journal entries with associated text, ambience (e.g., rain, cafe), and user IDs.
* **Instant Emotional Analysis:** Analyze individual entries to extract the dominant emotion, contextual keywords, and a brief summary.
* **User Insights:** Aggregate all entries for a specific user to determine their overall top emotion, most frequent ambience, and recent thematic keywords.
* **Smart Caching:** Repeated analysis of the exact same text is cached via Upstash Redis to reduce API latency and costs.
* **Rate Limiting:** API endpoints are protected against abuse (e.g., `5/minute` on the analyze endpoint).

## Local Development Setup

### Prerequisites
* Docker and Docker Compose
* Upstash Redis account & Token
* Gemini API Key

### Environment Variables
The application uses Docker Compose to manage environment variables. Update the `docker-compose.yml` with your actual credentials or create a `.env` file if running locally outside of Docker:
* `MONGO_URL`: Your MongoDB connection string.
* `GEMINI_API`: Your Gemini API key.
* `UPSTASH_TOKEN`: Your Upstash Redis token.

### Running the App
1. Clone the repository.
2. Build and start the containers using Docker Compose:
   ```bash
   docker-compose up --build