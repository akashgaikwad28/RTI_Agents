"""
mcp_clients/mongo_client.py
----------------------------
Production-grade async MongoDB client using motor.
Replaces the old synchronous pymongo implementation.
All database operations are fully async.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING
from datetime import datetime, timezone
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

_mongo_instance: "AsyncMongoClient | None" = None


class AsyncMongoClient:
    """
    Async MongoDB client (motor-based) for RTI-Agent.
    All operations are async-compatible with FastAPI.
    """

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self):
        """Initialize connection and create indexes."""
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True,
            )
            self.db = self.client[settings.MONGO_DB_NAME]
            # Verify connection
            await self.client.admin.command("ping")
            logger.info(f"[MongoDB] Connected to {settings.MONGO_DB_NAME}")
            await self._create_indexes()
        except Exception as e:
            logger.error(f"[MongoDB] Connection failed: {e}")
            raise

    async def _create_indexes(self):
        """Create production indexes for all collections."""
        try:
            # rti_requests indexes
            # users indexes
            await self.db["users"].create_indexes([
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("role", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ])
            await self.db["refresh_tokens"].create_indexes([
                IndexModel([("jti", ASCENDING)], unique=True),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),
            ])
            await self.db["rti_requests"].create_indexes([
                IndexModel([("tracking_id", ASCENDING)], unique=True, sparse=True),
                IndexModel([("request_id", ASCENDING)], unique=True),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("department", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("user_input.email", ASCENDING)]),
            ])
            # conversation_threads indexes
            await self.db["conversation_threads"].create_indexes([
                IndexModel([("thread_id", ASCENDING)], unique=True),
                IndexModel([("citizen_id", ASCENDING)]),
                IndexModel([("updated_at", DESCENDING)]),
            ])
            # audit_log indexes
            await self.db["audit_log"].create_indexes([
                IndexModel([("request_id", ASCENDING)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("action", ASCENDING)]),
            ])
            await self.db["documents_metadata"].create_indexes([
                IndexModel([("source_hash", ASCENDING)], unique=True, sparse=True),
                IndexModel([("source_url", ASCENDING)]),
                IndexModel([("department", ASCENDING)]),
                IndexModel([("document_type", ASCENDING)]),
                IndexModel([("language", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ])
            await self.db["scrape_history"].create_indexes([
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("payload.targets", ASCENDING)]),
            ])
            await self.db["rag_ingestion_logs"].create_indexes([
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("type", ASCENDING)]),
            ])
            await self.db["retrieval_analytics"].create_indexes([
                IndexModel([("created_at", DESCENDING)]),
                IndexModel([("department", ASCENDING)]),
                IndexModel([("confidence", DESCENDING)]),
            ])
            await self.db["adaptive_memory_events"].create_indexes([
                IndexModel([("request_id", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ])
            await self.db["reasoning_memory"].create_indexes([
                IndexModel([("request_id", ASCENDING)]),
            ])
            await self.db["correction_memory"].create_indexes([
                IndexModel([("request_id", ASCENDING)]),
            ])
            await self.db["learning_feedback"].create_indexes([
                IndexModel([("created_at", DESCENDING)]),
            ])
            await self.db["translation_memory"].create_indexes([
                IndexModel([("source_language", ASCENDING), ("target_language", ASCENDING)]),
                IndexModel([("source_text", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ])
            await self.db["crosslingual_history"].create_indexes([
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("language", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)]),
            ])
            logger.info("[MongoDB] Indexes created successfully")
        except Exception as e:
            logger.warning(f"[MongoDB] Index creation warning: {e}")

    async def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("[MongoDB] Connection closed")

    # ── RTI Requests ──────────────────────────────────────────────

    async def insert_rti_request(self, doc: dict) -> str:
        result = await self.db["rti_requests"].insert_one(doc)
        return str(result.inserted_id)

    async def get_rti_by_tracking_id(self, tracking_id: str) -> dict | None:
        return await self.db["rti_requests"].find_one({"tracking_id": tracking_id})

    async def get_rti_by_request_id(self, request_id: str) -> dict | None:
        return await self.db["rti_requests"].find_one({"request_id": request_id})

    async def update_rti_status(self, request_id: str, status: str, extra: dict = None):
        update = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if extra:
            update.update(extra)
        await self.db["rti_requests"].update_one(
            {"request_id": request_id},
            {"$set": update},
        )

    async def get_pending_approvals(self, limit: int = 50) -> list[dict]:
        cursor = self.db["rti_requests"].find(
            {"approval_status": "pending"}
        ).sort("created_at", DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)

    async def list_rtis(self, page: int = 1, limit: int = 10, filter_query: dict = None) -> list[dict]:
        skip = (page - 1) * limit
        cursor = self.db["rti_requests"].find(filter_query or {}).sort("created_at", DESCENDING).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_rtis(self, filter_query: dict = None) -> int:
        return await self.db["rti_requests"].count_documents(filter_query or {})

    # ── Conversation Threads ──────────────────────────────────────

    async def create_thread(self, thread_doc: dict) -> str:
        result = await self.db["conversation_threads"].insert_one(thread_doc)
        return str(result.inserted_id)

    async def get_thread(self, thread_id: str) -> dict | None:
        return await self.db["conversation_threads"].find_one({"thread_id": thread_id})

    async def append_message_to_thread(self, thread_id: str, message: dict):
        await self.db["conversation_threads"].update_one(
            {"thread_id": thread_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

    # ── Audit Log ─────────────────────────────────────────────────

    async def log_audit_event(self, request_id: str, action: str, details: dict = None):
        doc = {
            "request_id": request_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc),
        }
        await self.db["audit_log"].insert_one(doc)

    # ── Feedback ──────────────────────────────────────────────

    async def save_feedback(self, feedback_doc: dict):
        await self.db["feedback"].insert_one({
            **feedback_doc,
            "created_at": datetime.now(timezone.utc),
        })

    # ── Users (Auth) ──────────────────────────────────────────────

    async def create_user(self, doc: dict) -> str:
        """Insert a new user document. Returns the string id."""
        result = await self.db["users"].insert_one(doc)
        return str(result.inserted_id)

    async def get_user_by_email(self, email: str) -> dict | None:
        return await self.db["users"].find_one({"email": email.lower()})

    async def get_user_by_id(self, user_id: str) -> dict | None:
        from bson import ObjectId
        try:
            return await self.db["users"].find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    async def update_user(self, user_id: str, patch: dict):
        from bson import ObjectId
        patch["updated_at"] = datetime.now(timezone.utc)
        await self.db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": patch},
        )

    async def list_users(self, skip: int = 0, limit: int = 50) -> list[dict]:
        cursor = self.db["users"].find({}, {"hashed_password": 0}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_users(self) -> int:
        return await self.db["users"].count_documents({})

    # ── Refresh Token Blacklist ────────────────────────────────────

    async def save_refresh_token(self, jti: str, user_id: str, expires_at: datetime):
        """Persist a refresh token JTI for revocation tracking."""
        await self.db["refresh_tokens"].insert_one({
            "jti": jti, "user_id": user_id, "expires_at": expires_at,
            "revoked": False, "created_at": datetime.now(timezone.utc),
        })

    async def revoke_refresh_token(self, jti: str):
        """Mark a refresh token as revoked."""
        await self.db["refresh_tokens"].update_one({"jti": jti}, {"$set": {"revoked": True}})

    async def is_refresh_token_revoked(self, jti: str) -> bool:
        doc = await self.db["refresh_tokens"].find_one({"jti": jti})
        if not doc:
            return True  # Unknown token = treat as revoked
        return doc.get("revoked", False)


async def get_mongo_client() -> AsyncMongoClient:
    """Returns the singleton async MongoDB client."""
    global _mongo_instance
    if _mongo_instance is None:
        _mongo_instance = AsyncMongoClient()
        await _mongo_instance.connect()
    return _mongo_instance
