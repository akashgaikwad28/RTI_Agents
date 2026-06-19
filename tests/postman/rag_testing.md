# RAG Knowledge Ingestion & Retrieval API Testing

This guide explains how to test the Retrieval-Augmented Generation (RAG) pipelines, indexing crawlers, semantic search lookups, and document version history controls inside the **RAG Knowledge Base** folder.

---

## 🧠 The RAG Architecture

The RTI-Agent backend supports two interchangeable high-performance vector databases configured via the `.env` variable **`VECTORSTORE_TYPE`**:
1. **`faiss`**: Local, ultra-fast vector index stored on disk in the `data/vector_store` directory.
2. **`mongodb`**: Production-grade cloud vector store (MongoDB Atlas Vector Search) using the `$vectorSearch` aggregation pipeline.

The testing suite validates both configurations transparently.

---

## 📋 Step-by-Step API Testing Workflows

Here are the verification procedures for RAG endpoints:

### 1. Document Ingestion Pipeline
*   **Request**: `POST /api/v1/rag/ingest`
*   **Purpose**: Indexes new reference texts (circulars, policies, rules) into the active vectorstore.
*   **Body Example**:
    ```json
    {
      "document_name": "smart_city_pune_budget_2024.pdf",
      "content": "Pune Smart City transport allocation: 600 Crores, solid waste: 400 Crores, IT: 500 Crores.",
      "department": "Urban Development",
      "metadata": {"source": "Government Circular", "year": "2024"}
    }
    ```
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert the response includes a generated `document_id`.
    *   **Postman Script**: Automatically extracts and saves the `document_id` to the environment variable **`DOCUMENT_ID`** for subsequent auditing tests.

### 2. Portal Scraper Web Crawler
*   **Request**: `POST /api/v1/rag/scrape`
*   **Purpose**: Triggers the system's asynchronous web crawler to scrape and index government portals.
*   **Body Example**:
    ```json
    {
      "url": "https://www.maharashtra.gov.in/smart-city-schemes",
      "depth": 1,
      "max_pages": 5
    }
    ```
*   **Postman Automated Tests**:
    *   Assert status is `200 OK` or `202 Accepted`.
    *   Verify the return payload contains a `status` (started/completed) and `pages_scraped`.

### 3. Direct RAG Semantic Query Testing
*   **Request**: `POST /api/v1/rag/query-test`
*   **Purpose**: Runs a isolated similarity search against the active vector index (excluding agents) to verify that embeddings generation and cosine similarities are operational.
*   **Body Example**:
    ```json
    {
      "query_text": "smart city pune budget transport",
      "top_k": 3
    }
    ```
*   **Postman Automated Tests**:
    *   Assert status is `200 OK`.
    *   Assert the response contains a `results` array of matching chunks, showing content, source metadata, and similarity score.

### 4. Cross-Lingual Semantic Queries
*   **Request**: `POST /api/v1/rag/multilingual-query`
*   **Purpose**: Submits queries in regional languages (e.g., Marathi), translates them, performs searches, and retrieves matching records.
*   **Body Example**:
    ```json
    {
      "query_text": "पुणे स्मार्ट सिटी वाहतूक खर्च",
      "language": "mr",
      "top_k": 3
    }
    ```

### 5. Document Versioning & Audit History
*   **Requests**:
    *   `GET /api/v1/rag/document-history/{{DOCUMENT_ID}}`
    *   `GET /api/v1/rag/document-version/{{DOCUMENT_ID}}/1`
*   **Purpose**: Audits how document content has evolved over time. If a document is updated, the database stores previous snapshot versions in MongoDB.
*   **Expected Results**: History logs all edit actions, timestamps, and active editors. Version details fetch the exact text snapshot of version 1.

### 6. RAG Corpus Health Check
*   **Request**: `GET /api/v1/rag/corpus-health`
*   **Purpose**: Audit tool that checks the overall vector database consistency:
    *   Embedding dimensionality integrity (e.g., matching Gemini `768` or Groq dimensions).
    *   Empty/Null content flags.
    *   Index fragmentation checks.
*   **Postman Test Script**: Asserts status is `200 OK` and reads `{"status": "healthy"}`.
