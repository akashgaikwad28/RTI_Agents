"""
tests/verify_cloud_db.py
-------------------------
End-to-end cloud database connectivity verification script for RTI-Agent.
Tests MongoDB Atlas, Upstash Redis, and Neon PostgreSQL connections.
"""

import asyncio
import os
import sys
import time

# Set Windows Selector Event Loop Policy for Psycopg async on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Ensure project root is in python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)


async def verify_mongodb():
    logger.info("📡 Testing MongoDB Atlas connection...")
    from mcp_clients.mongo_client import get_mongo_client
    
    # Try up to 3 times to account for transient replica set elections or network timeouts
    for attempt in range(1, 4):
        try:
            logger.info(f"  Connection attempt {attempt}/3...")
            mongo = await get_mongo_client()
            
            # Perform a write test
            test_collection = mongo.db["_connectivity_test"]
            test_doc = {"test_key": "connectivity_ok", "timestamp": time.time()}
            
            # Insert
            insert_result = await test_collection.insert_one(test_doc)
            doc_id = insert_result.inserted_id
            logger.info(f"  [OK] Successfully wrote to MongoDB on attempt {attempt}. Document ID: {doc_id}")
            
            # Find
            found = await test_collection.find_one({"_id": doc_id})
            assert found is not None and found["test_key"] == "connectivity_ok"
            logger.info("  [OK] Successfully read from MongoDB.")
            
            # Delete
            await test_collection.delete_one({"_id": doc_id})
            logger.info("  [OK] Successfully cleaned up MongoDB test document.")
            
            logger.info("🟢 MongoDB Atlas: CONNECTIVITY VERIFIED SUCCESSFUL!")
            return True
        except Exception as e:
            logger.warning(f"  [WARN] Attempt {attempt} failed: {e}")
            if attempt < 3:
                await asyncio.sleep(2)
            else:
                logger.error("🔴 MongoDB Atlas connection failed after 3 attempts.")
                return False


async def verify_redis():
    logger.info("📡 Testing Upstash Redis connection...")
    from rag.vectorstore.semantic_cache import get_semantic_cache
    try:
        cache = await get_semantic_cache()
        if not cache.is_available:
            raise RuntimeError("Redis cache reported as unavailable (degraded mode)")
        
        # Ping
        ping_ok = await cache._client.ping()
        logger.info(f"  [OK] Ping returned: {ping_ok}")
        
        # Write
        test_key = "rti:connectivity_test"
        await cache.set(test_key, "redis_ok", ttl=10)
        logger.info("  [OK] Successfully wrote test key to Upstash Redis.")
        
        # Read
        val = await cache.get(test_key)
        assert val == "redis_ok"
        logger.info("  [OK] Successfully read test key from Upstash Redis.")
        
        # Delete
        await cache.delete(test_key)
        logger.info("  [OK] Successfully deleted test key from Upstash Redis.")
        
        logger.info("🟢 Upstash Redis: CONNECTIVITY VERIFIED SUCCESSFUL!")
        return True
    except Exception as e:
        logger.error(f"🔴 Upstash Redis connection failed: {e}")
        return False


async def verify_postgres():
    logger.info("📡 Testing Neon PostgreSQL checkpointer connection...")
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from langgraph.graph import StateGraph, START, END
    try:
        if not settings.POSTGRES_CHECKPOINTER_URL:
            logger.warning("  [WARN] POSTGRES_CHECKPOINTER_URL is not set.")
            return False
            
        async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_CHECKPOINTER_URL) as saver:
            await saver.setup()
            logger.info("  [OK] Successfully verified Neon PostgreSQL checkpoint tables setup.")
            
            from typing import TypedDict
            class TestState(TypedDict):
                input: str
                result: str
                
            # Compile a minimal StateGraph using Neon PostgreSQL checkpointer
            builder = StateGraph(TestState)
            builder.add_node("dummy", lambda state: {"result": "postgres_checkpoint_ok", "input": state.get("input", "")})
            builder.add_edge(START, "dummy")
            builder.add_edge("dummy", END)
            
            graph = builder.compile(checkpointer=saver)
            logger.info("  [OK] Minimal StateGraph compiled successfully with Postgres checkpointer.")
            
            # Execute the graph to trigger checkpointer saves
            config = {"configurable": {"thread_id": f"connectivity_test_{int(time.time())}"}}
            res = await graph.ainvoke({"input": "test"}, config=config)
            logger.info(f"  [OK] Graph execution complete. Result: {res}")
            
            # Retrieve state back from checkpointer to verify loading
            state = await graph.aget_state(config)
            assert state is not None
            assert state.values.get("result") == "postgres_checkpoint_ok"
            logger.info("  [OK] Graph state successfully retrieved from Postgres checkpointer.")
            
        logger.info("🟢 Neon PostgreSQL: CONNECTIVITY VERIFIED SUCCESSFUL!")
        return True
    except Exception as e:
        logger.error(f"🔴 Neon PostgreSQL connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    logger.info("=========================================")
    logger.info("  RTI-AGENT CLOUD CONNECTIVITY DIAGNOSTICS")
    logger.info("=========================================")
    
    mongo_ok = await verify_mongodb()
    redis_ok = await verify_redis()
    pg_ok = await verify_postgres()
    
    logger.info("=========================================")
    if mongo_ok and redis_ok and pg_ok:
        logger.info("🎉 SUCCESS: ALL CLOUD DATABASES CONNECTED AND WORKING!")
        sys.exit(0)
    else:
        logger.error("❌ FAILURE: SOME CLOUD DATABASES FAILED CONNECTIVITY CHECKS.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
