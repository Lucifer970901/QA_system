# 💬 Member Data Question-Answering (QA) API

## 🎯 1. Problem Understanding

The goal of this project is to create a real-time **Question-Answering (QA) API** that can respond to natural-language queries about member data. This data is sourced from an **unstructured public `/messages` API endpoint**.

The core challenge is to **extract and infer structured answers** (e.g., dates, counts, names) from raw, unstructured human language messages, and deliver the result via a simple `/ask` API endpoint.

| Example Query | Targeted Extraction/Inference |
| :--- | :--- |
| **"When is Layla planning her trip to London?"** | **Member:** Layla, **Intent:** Trip, **Answer:** Date/Time |
| **"How many cars does Vikram Desai have?"** | **Member:** Vikram Desai, **Intent:** Cars, **Answer:** Count |
| **"What are Amira’s favorite restaurants?"** | **Member:** Amira, **Intent:** Restaurants, **Answer:** List of places |

---

## 🏛️ 2. Overall System Architecture

The service is designed as a pipeline that processes a natural language query through several asynchronous layers before returning the final JSON answer.

```mermaid
graph TD
    A[User Query <br> (Natural Language Input)] --> B[/ask Endpoint (API) <br> FastAPI Web Server]
    B --> C[Question Parser <br> - Extracts member name + intent]
    C --> D[Data Retrieval Layer <br> - Calls /messages API <br> - Normalizes content]
    D --> E[Inference Engine <br> - Keyword matching <br> - Rule-based logic <br> - (Optional) semantic similarity]
    E --> F{JSON Response <br> {"answer": "..."}}
---

## ⚙️ 3. Key Design Components

### A. API Layer (FastAPI)

* **Endpoint:** Exposes a single `/ask` endpoint via **HTTP GET**.
* **Request:** Accepts the user question as a query parameter (e.g., `?question=...`).
* **Response:** Returns a JSON object in the format: `{"answer": "..."}`.
* **Technology:** Uses **FastAPI** for its asynchronous nature, which is ideal for I/O-bound tasks like external API calls.
* **Deployment:** Lightweight and easily deployable on serverless platforms (Google Cloud Run, Render, Railway).
* **Features:** Handles validation, exception handling, and CORS out-of-the-box.

### B. Data Retrieval Layer

* **Source Connection:** Connects directly to the public `/messages` endpoint.
* **Freshness:** Fetches messages **dynamically on each query** to ensure the most up-to-date data.
* **Optimization:** A simple **caching mechanism (optional)** is used to avoid redundant network calls for identical recent queries.
* **Normalization:** Cleanses the data for reliable text matching:
    * Converts all text to **lowercase**.
    * Strips punctuation.
    * Removes emojis.

### C. NLP / Question Understanding (Parser)

The system uses a **lightweight, rule-based NLP** approach for fast processing:

1.  **Entity Extraction:** **Regex** is used to identify capitalized patterns, which are highly probable indicators of member names (e.g., `Layla`, `Vikram Desai`).
2.  **Intent Detection:** **Keyword-based matching** identifies the question type (e.g., `trip`, `car`, `restaurant`, `travel`).
3.  **Fallback Logic:** If both entity and intent are ambiguous or missing, a generic response is prepared.

### D. Inference Engine (Contextual Search)

The engine implements robust contextual search logic:

1.  **Filter:** Isolate all normalized messages mentioning the **extracted member name**.
2.  **Search:** Look for message content that contains keywords related to the question’s **intent**.
3.  **Answer Generation:** Return the **best-matched message content** as the definitive "answer."
4.  **Fallback:** If no direct, relevant message is found, return a **friendly fallback** (e.g., “No trip information found for Layla.”).

---

## ⚠️ 4. Error Handling & Edge Cases

The system is designed for high resilience and user-friendly communication during failures.

* **No Member Detected:** "Sorry, I couldn’t identify the member’s name."
* **No Related Message:** "No data found for this member."
* **Empty Question:** Returns **HTTP 400 Bad Request** with a validation message.
* **Network Error:** Gracefully handled; returns a user-friendly JSON error response instead of a server crash.
* **Text Matching:** Robustly handles **case and punctuation insensitivity** via the data normalization process.

---

## 🔒 5. Security & Performance

### Security
* **Method Restriction:** Only the **GET** method is supported, minimizing the attack surface.
* **Transport:** All external requests use **HTTPS**.
* **Input Sanitization:** Input queries are sanitized against common vulnerabilities like code injection.

### Performance
* **Target Latency:** Average response time is targeted to be **< 500 ms** (for typical message loads, e.g., < 1000 messages).
* **Scalability:** Deployment on platforms like **Cloud Run** provides automatic scaling to support parallel user requests efficiently.

---

## ✅ 6. Testing Strategy

| Test Type | Objective | Key Scenarios |
| :--- | :--- | :--- |
| **Unit Tests** | Verify core component logic. | Member extraction (regex accuracy), Intent detection (keyword mapping), and Inference logic (correct message snippet return). |
| **Integration Tests** | Validate end-to-end API flow. | Mock the external `/messages` API response and validate the `/ask` endpoint's JSON output for various sample questions. |
| **Edge Case Tests** | Ensure failure resilience. | Missing member name, non-existent topics, queries with multiple possible matches, and testing API with empty/invalid questions. |