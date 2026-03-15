### `ARCHITECTURE.md`
```markdown
# System Architecture & Scaling Strategy

This document outlines the current architecture of the Arvyax Journaling application and details the roadmap for scaling, cost reduction, and security.

## Current Architecture
The application follows a standard client-server model:
* A **React frontend** communicates via REST API.
* A **FastAPI backend** handles business logic, rate limiting, and caching.
* **MongoDB** persists the journal entries.
* **Upstash Redis** acts as a distributed cache for LLM responses.
* **Gemini API** provides the natural language processing for emotional analysis.

---

## How would you scale this to 100k users?

To support 100,000 active users, the current synchronous architecture needs to be decentralized and made fully asynchronous.

1. **Database Optimization:**
   * **Indexing:** Add an index on `userId` in the `journal` MongoDB collection to optimize the `GET /api/journal/{userId}` and `GET /api/journal/insights/{userId}` queries.
   * **Connection Pooling:** Ensure the FastAPI app leverages MongoDB connection pooling effectively to handle concurrent database requests.
2. **Decoupling LLM Calls (Message Queues):**
   * Currently, the `/api/journal/analyze` and `/insights` endpoints wait synchronously for the Gemini API to respond. Under heavy load, this will exhaust Uvicorn worker threads.
   * **Solution:** Implement a message broker (like RabbitMQ, Apache Kafka, or Redis Queues/Celery). The API should accept the request, push the job to a queue, and return a `202 Accepted` status. Background workers will process the LLM calls and push the results to the database or a WebSocket connection.
3. **Horizontal Scaling:**
   * Deploy the FastAPI backend across multiple instances using Kubernetes or AWS ECS, fronted by an Application Load Balancer.
4. **Pagination:**
   * The `GET /api/journal/{userId}` endpoint currently returns *all* entries. This must be paginated to prevent memory exhaustion on both the backend and frontend client as users accumulate hundreds of entries.

## How would you reduce LLM cost?

1. **Model Optimization:** * The system currently uses `gemini-2.5-flash`, which is cost-effective. Stick with Flash variants rather than Pro variants for simple emotion and keyword extraction tasks.
2. **Limit Context Windows for Insights:**
   * The `GET /api/journal/insights/{userId}` endpoint sends *all* historical user text to the LLM in a single prompt. For a user with years of entries, this will result in massive token usage and increased costs.
   * **Solution:** Only send the last *N* entries (e.g., the last 30 days or the last 20 entries) to the LLM for recent insights, rather than the entire database history.
3. **Prompt Engineering:**
   * Optimize system prompts to be as concise as possible to reduce input token count. 

## How would you cache repeated analysis?

The system already utilizes Upstash Redis to cache exact text matches for the `analyze` endpoint. To improve this further:

1. **Insight Caching:**
   * The `/insights` endpoint is currently entirely uncached. Run the insights analysis and cache the resulting JSON object in Redis using the `userId` as the key.
   * **Invalidation Strategy:** Invalidate or update the cached insights object whenever a user triggers the `POST /api/journal` endpoint to create a new entry.
2. **Semantic Caching:**
   * Exact text caching (currently implemented) fails if the user adds a single punctuation mark. Implement text normalization (lowercasing, stripping special characters) before checking the Redis cache to improve the cache hit rate.

## How would you protect sensitive journal data?

Journal entries contain highly sensitive, personal thoughts. The current implementation stores plaintext data and accepts user IDs directly from the client.

1. **Authentication & Authorization:**
   * Remove the client-side `userId` state (`"123"`). Implement robust authentication (e.g., OAuth 2.0, JWT). The backend must extract the `userId` securely from the JWT payload to ensure users can only access their own entries.
2. **Data Encryption (At Rest & Application Level):**
   * Enable encryption at rest in the MongoDB deployment.
   * Implement **Application-Level Envelope Encryption**. The backend should encrypt the `text` field using a library like AWS KMS or HashiCorp Vault *before* saving it to MongoDB, ensuring that even direct database access does not expose user journals.
3. **Data Sanitization Before LLM Processing:**
   * Before sending journal text to the Gemini API, pipe the text through a PII (Personally Identifiable Information) scrubber (like Microsoft Presidio) to mask names, phone numbers, and locations.