"""
mongo_client.py
----------------
Production-ready MongoDB client for RTI Agent system.
Handles connection, insertion, updates, and retrieval of RTI requests.
Uses centralized logger and exception handler utilities.
"""

from pymongo import MongoClient, errors
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv
from utils.logger import logger
from utils.exception_handler import exception_handler
from schemas.rti_query_schema import RTIRequestSchema
from typing import Optional, Dict

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
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True,
            )

            # Check connection on init
            self.client.admin.command("ping")

            self.db = self.client[db_name]
            self.collection = self.db["rti_requests"]

            logger.info(f"Connected to MongoDB: {db_name}")

        except errors.ServerSelectionTimeoutError as e:
            exception_handler(e, "MongoDB connection timed out.")
            raise
        except Exception as e:
            exception_handler(e, "Error initializing MongoDB client.")
            raise

    def insert_rti_request(self, data: dict):
        try:
            validated_data = RTIRequestSchema(**data).dict()
            validated_data["created_at"] = datetime.utcnow()
            validated_data["updated_at"] = datetime.utcnow()

            result = self.collection.insert_one(validated_data)
            logger.info(f" Inserted RTI Request with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            exception_handler(e, "Error inserting RTI request.")
            return None

    def update_formatted_query(self, request_id: str, formatted_query: str):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {"formatted_query": formatted_query, "updated_at": datetime.utcnow()}},
            )
            logger.info(
                f" Updated formatted query for ID: {request_id}, matched: {result.matched_count}"
            )
            return result.modified_count
        except Exception as e:
            exception_handler(e, f"Error updating formatted query for ID {request_id}.")
            return 0

    def update_department(self, request_id: str, department: str):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {"department": department, "updated_at": datetime.utcnow()}},
            )
            logger.info(
                f" Updated department for ID: {request_id}, matched: {result.matched_count}"
            )
            return result.modified_count
        except Exception as e:
            exception_handler(e, f"Error updating department for ID {request_id}.")
            return 0

    def get_rti_request(self, request_id: str):
        try:
            doc = self.collection.find_one({"_id": ObjectId(request_id)})
            if not doc:
                logger.warning(f"No RTI request found with ID: {request_id}")
            else:
                logger.info(f" Retrieved RTI request ID: {request_id}")
            return doc
        except Exception as e:
            exception_handler(e, f"Error retrieving RTI request ID {request_id}.")
            return None

    def get_pending_requests(self):
        try:
            pending = list(self.collection.find({"status": "pending"}))
            logger.info(f" Fetched {len(pending)} pending RTI requests.")
            return pending
        except Exception as e:
            exception_handler(e, "Error fetching pending RTI requests.")
            return []

    def get_all_requests(self, limit: int = 50):
        try:
            requests = list(self.collection.find().limit(limit))
            logger.info(f" Retrieved {len(requests)} total RTI requests.")
            return requests
        except Exception as e:
            exception_handler(e, "Error fetching all RTI requests.")
            return []

   
    def get_info_by_query(self, query_text: str) -> Optional[dict]:
        """
        Retrieve cached info for a given formal query, if it exists.
        """
        try:
            doc = self.collection.find_one({"formal_query": query_text})
            if doc:
                logger.info(f"Found cached info for query: {query_text}")
            else:
                logger.info(f"No cached info for query: {query_text}")
            return doc
        except Exception as e:
            exception_handler(e, f"Error fetching cached info for query: {query_text}")
            return None

    def save_info(self, query: str, info: str):
        """
        Save fetched info for a given query to MongoDB.
        Creates a new document if it doesn't exist.
        """
        try:
            result = self.collection.update_one(
                {"formal_query": {"$regex": query, "$options": "i"}},
                {"$set": {"info": info, "updated_at": datetime.utcnow()}},
                upsert=True,
            )
            logger.info(f" Saved info for query: {query}, modified: {result.modified_count}")
            return True
        except Exception as e:
            exception_handler(e, f"Error saving info for query: {query}")
            return False

    def close_connection(self):
        try:
            self.client.close()
            logger.info(" MongoDB connection closed successfully.")
        except Exception as e:
            exception_handler(e, "Error closing MongoDB connection.")


# Create a singleton instance
mongo_client = MongoDBClient()
