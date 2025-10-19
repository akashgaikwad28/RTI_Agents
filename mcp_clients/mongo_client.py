"""
mongo_client.py
----------------
Production-ready MongoDB client for RTI Agent system.
Handles connection, insertion, updates, and retrieval of RTI requests.
Uses custom logger and centralized exception handling.
"""

from pymongo import MongoClient, errors
from datetime import datetime
import os
from dotenv import load_dotenv
from utils.logger import logger
from utils.exception_handler import handle_exception
from schemas.rti_request_schema import RTIRequestSchema

load_dotenv()


class MongoDBClient:
    """
    Handles all MongoDB interactions for RTI Agent.
    """

    def __init__(self):
        try:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            db_name = os.getenv("MONGO_DB_NAME", "rti_db")
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # timeout in ms
                connectTimeoutMS=5000,
                retryWrites=True,
            )
            self.db = self.client[db_name]
            self.collection = self.db["rti_requests"]
            logger.info(f"✅ Connected to MongoDB: {db_name}")
        except errors.ConnectionFailure as e:
            handle_exception(e)
            raise
        except Exception as e:
            handle_exception(e)
            raise

    # ───────────────────────────────────────────────────────────────
    # 🧩 CORE METHODS
    # ───────────────────────────────────────────────────────────────
    def insert_rti_request(self, data: dict):
        """
        Insert a new RTI request document.
        - Validates schema via Pydantic model (RTIRequestSchema)
        - Logs insertion result
        """
        try:
            validated_data = RTIRequestSchema(**data).dict()
            result = self.collection.insert_one(validated_data)
            logger.info(f"Inserted RTI Request with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            handle_exception(e)
            return None

    def update_formatted_query(self, request_id: str, formatted_query: str):
        """
        Update the formatted query field for an RTI request.
        """
        from bson import ObjectId
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {"formatted_query": formatted_query, "updated_at": datetime.utcnow()}},
            )
            logger.info(f"Updated formatted query for ID: {request_id}, matched: {result.matched_count}")
            return result.modified_count
        except Exception as e:
            handle_exception(e)
            return 0

    def update_department(self, request_id: str, department: str):
        """
        Update the department classification for an RTI request.
        """
        from bson import ObjectId
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {"department": department, "updated_at": datetime.utcnow()}},
            )
            logger.info(f"Updated department for ID: {request_id}, matched: {result.matched_count}")
            return result.modified_count
        except Exception as e:
            handle_exception(e)
            return 0

    def get_rti_request(self, request_id: str):
        """
        Retrieve a single RTI request by ID.
        """
        from bson import ObjectId
        try:
            doc = self.collection.find_one({"_id": ObjectId(request_id)})
            if not doc:
                logger.warning(f"No RTI request found with ID: {request_id}")
            else:
                logger.info(f"Retrieved RTI request ID: {request_id}")
            return doc
        except Exception as e:
            handle_exception(e)
            return None

    def get_pending_requests(self):
        """
        Retrieve all RTI requests with status='pending'.
        """
        try:
            pending = list(self.collection.find({"status": "pending"}))
            logger.info(f"Fetched {len(pending)} pending RTI requests.")
            return pending
        except Exception as e:
            handle_exception(e)
            return []

    def close_connection(self):
        """
        Gracefully close MongoDB connection.
        """
        try:
            self.client.close()
            logger.info("🔒 MongoDB connection closed successfully.")
        except Exception as e:
            handle_exception(e)
