"""
tests/verify_mongo_vector.py
----------------------------
Connection and operations diagnostics for Cloud MongoDB Vector Store.
"""

import asyncio
import os
import sys
import time

# Ensure project root is in python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings
from observability.structured_logger import get_logger
from rag.types import DocumentChunk, DocumentMetadata

logger = get_logger(__name__)


async def main():
    logger.info("=========================================")
    logger.info("  RTI-AGENT CLOUD VECTOR STORE DIAGNOSTICS")
    logger.info("=========================================")

    # Force vector store to mongodb for diagnostic run
    settings.VECTORSTORE_TYPE = "mongodb"
    
    from rag.vectorstore import get_vector_store
    store = get_vector_store()
    
    logger.info("📡 Testing MongoDB connection & retrieving collection...")
    try:
        collection = await store._get_collection()
        logger.info(f"  [OK] Collection retrieved: {collection.name}")
    except Exception as e:
        logger.error(f"🔴 MongoDB connection failed: {e}")
        sys.exit(1)

    logger.info("📡 Clearing previous connectivity test data...")
    try:
        # Clean previous diagnostic documents starting with 'test_chk_'
        await collection.delete_many({"chunk_id": {"$regex": "^test_chk_"}})
        logger.info("  [OK] Old test chunks cleared.")
    except Exception as e:
        logger.error(f"🔴 Delete operation failed: {e}")
        sys.exit(1)

    logger.info("📡 Ingesting clean test document chunks...")
    try:
        # Create mock chunks
        chunk1 = DocumentChunk(
            chunk_id="test_chk_1",
            chunk_index=0,
            text="The road construction budget for Pune Municipal Corporation in 2026 is 500 Crore Rupees, allocated under infrastructure development.",
            content_hash="hash_pune_budget",
            metadata=DocumentMetadata(
                document_id="test_doc_pune",
                title="Pune Infra Budget 2026",
                document_type="budget",
                department="Public Works Department",
                language="en",
                page_number=1
            )
        )
        
        chunk2 = DocumentChunk(
            chunk_id="test_chk_2",
            chunk_index=1,
            text="Under the RTI Act section 6(1), citizens have the right to request public records from any municipal department.",
            content_hash="hash_rti_act",
            metadata=DocumentMetadata(
                document_id="test_doc_rti",
                title="RTI Right to Information Handbook",
                document_type="handbook",
                department="General Administration",
                language="en",
                page_number=3
            )
        )

        res = await store.aadd_chunks([chunk1, chunk2])
        logger.info(f"  [OK] Ingested document chunks successfully. Result: {res}")
        assert res["indexed"] == 2
    except Exception as e:
        logger.error(f"🔴 Document ingestion failed: {e}")
        sys.exit(1)

    logger.info("📡 Running similarity search query with filters (Budget)...")
    try:
        results = await store.asimilarity_search_with_score(
            query="pune municipal road budget",
            k=2,
            filters={"department": "Public Works Department"}
        )
        logger.info(f"  [OK] Search results returned: {len(results)} items.")
        
        for i, (result, distance) in enumerate(results, 1):
            logger.info(f"    Result #{i}: score={result.score:.4f} source={result.source}")
            logger.info(f"      Text: {result.text[:100]}...")
            logger.info(f"      Citation: {result.citation}")
            
        assert len(results) > 0
        assert results[0][0].metadata.document_id == "test_doc_pune"
        logger.info("  [OK] Similarity search and metadata filtering asserted successfully!")
    except Exception as e:
        logger.error(f"🔴 Similarity search failed: {e}")
        sys.exit(1)

    logger.info("📡 Cleaning up connectivity test data...")
    try:
        await collection.delete_many({"chunk_id": {"$regex": "^test_chk_"}})
        logger.info("  [OK] Test data cleared successfully.")
    except Exception as e:
        logger.warning(f"  [WARN] Failed to clear test data: {e}")

    logger.info("=========================================")
    logger.info("🎉 SUCCESS: CLOUD VECTOR STORE IS WORKING!")
    logger.info("=========================================")


if __name__ == "__main__":
    asyncio.run(main())
