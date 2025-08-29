from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import get_settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)

# Global variables for MongoDB connection
_client: Optional[MongoClient] = None
_database: Optional[Database] = None
_connection_initialized = False

def get_client() -> MongoClient:
    """Get MongoDB client instance with lazy initialization"""
    global _client, _connection_initialized
    if _client is None or not _connection_initialized:
        settings = get_settings()
        try:
            # Close existing connection if any
            if _client:
                try:
                    _client.close()
                except Exception:
                    pass  # Ignore close errors
            
            # Create new connection with proper settings
            _client = MongoClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=20,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                retryWrites=True,
                retryReads=True
            )
            
            # Test the connection
            _client.admin.command('ping')
            _connection_initialized = True
            logger.info(f"Connected to MongoDB at {settings.mongodb_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            _client = None
            _connection_initialized = False
            raise
    return _client

def get_database() -> Database:
    """Get MongoDB database instance"""
    global _database
    if _database is None:
        settings = get_settings()
        _database = get_client()[settings.mongodb_database]
        logger.info(f"Using database: {settings.mongodb_database}")
    return _database

def get_collection(collection_name: str) -> Collection:
    """Get MongoDB collection instance"""
    return get_database()[collection_name]

# Collection names
ANALYSIS_TASKS_COLLECTION = "analysis_tasks"
MODEL_USAGE_COLLECTION = "model_usage"

class MongoDBManager:
    """Manager class for MongoDB operations"""
    
    @staticmethod
    async def init_db():
        """Initialize database and create indexes"""
        try:
            db = get_database()
            
            # Create indexes for analysis_tasks collection
            analysis_tasks = db[ANALYSIS_TASKS_COLLECTION]
            analysis_tasks.create_index("id", unique=True)
            analysis_tasks.create_index("status")
            analysis_tasks.create_index("created_at")
            
            # Create indexes for model_usage collection
            model_usage = db[MODEL_USAGE_COLLECTION]
            model_usage.create_index("task_id")
            model_usage.create_index("created_at")
            
            logger.info("MongoDB initialized successfully with indexes")
            
            # Run data migration for existing data
            await MongoDBManager.migrate_existing_data()
            
        except Exception as e:
            logger.error(f"MongoDB initialization failed: {e}")
            raise
    
    @staticmethod
    async def close_connection():
        """Close MongoDB connection"""
        global _client, _database, _connection_initialized
        try:
            if _client:
                _client.close()
                logger.info("MongoDB connection closed")
            _client = None
            _database = None
            _connection_initialized = False
        except Exception as e:
            logger.warning(f"Error closing MongoDB connection: {e}")
            # Reset state even if close fails
            _client = None
            _database = None
            _connection_initialized = False

    @staticmethod
    async def migrate_existing_data():
        """Migrate existing data to fix data type issues"""
        try:
            collection = get_collection(ANALYSIS_TASKS_COLLECTION)
            
            # Find all documents with analysis_summary as dict
            cursor = collection.find({"analysis_summary": {"$type": "object"}})
            count = 0
            
            for doc in cursor:
                if isinstance(doc.get("analysis_summary"), dict):
                    # Convert dict to JSON string
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"analysis_summary": json.dumps(doc["analysis_summary"])}}
                    )
                    count += 1
            
            if count > 0:
                logger.info(f"Migrated {count} documents with analysis_summary data type")
            
            # Find all documents with detected_languages as array
            cursor = collection.find({"detected_languages": {"$type": "array"}})
            count = 0
            
            for doc in cursor:
                if isinstance(doc.get("detected_languages"), list):
                    # Convert list to JSON string
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"detected_languages": json.dumps(doc["detected_languages"])}}
                    )
                    count += 1
            
            if count > 0:
                logger.info(f"Migrated {count} documents with detected_languages data type")
            
            # Add missing test_generation_data and coverage_results_data fields for existing completed tasks
            cursor = collection.find({
                "status": "completed",
                "$or": [
                    {"test_generation_data": {"$exists": False}},
                    {"coverage_results_data": {"$exists": False}}
                ]
            })
            count = 0
            
            for doc in cursor:
                update_data = {}
                
                # Add test_generation_data if missing
                if "test_generation_data" not in doc:
                    update_data["test_generation_data"] = json.dumps({})
                
                # Add coverage_results_data if missing
                if "coverage_results_data" not in doc:
                    update_data["coverage_results_data"] = json.dumps({})
                
                if update_data:
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": update_data}
                    )
                    count += 1
            
            if count > 0:
                logger.info(f"Added missing fields to {count} existing completed tasks")
                
        except Exception as e:
            logger.error(f"Error during data migration: {e}")
            raise

# MongoDB operations for analysis tasks
class AnalysisTaskManager:
    """Manager for analysis task operations"""
    
    @staticmethod
    def create_task(task_data: Dict[str, Any]) -> str:
        """Create a new analysis task"""
        collection = get_collection(ANALYSIS_TASKS_COLLECTION)
        result = collection.insert_one(task_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        collection = get_collection(ANALYSIS_TASKS_COLLECTION)
        return collection.find_one({"id": task_id})
    
    @staticmethod
    def update_task(task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a task"""
        collection = get_collection(ANALYSIS_TASKS_COLLECTION)
        result = collection.update_one(
            {"id": task_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_tasks_by_status(status: str) -> list:
        """Get tasks by status"""
        collection = get_collection(ANALYSIS_TASKS_COLLECTION)
        return list(collection.find({"status": status}))
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """Delete a task"""
        collection = get_collection(ANALYSIS_TASKS_COLLECTION)
        result = collection.delete_one({"id": task_id})
        return result.deleted_count > 0

# MongoDB operations for model usage
class ModelUsageManager:
    """Manager for model usage operations"""
    
    @staticmethod
    def create_usage_record(usage_data: Dict[str, Any]) -> str:
        """Create a new model usage record"""
        collection = get_collection(MODEL_USAGE_COLLECTION)
        result = collection.insert_one(usage_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_usage_by_task(task_id: str) -> list:
        """Get usage records for a specific task"""
        collection = get_collection(MODEL_USAGE_COLLECTION)
        return list(collection.find({"task_id": task_id}))
    
    @staticmethod
    def get_total_usage() -> Dict[str, Any]:
        """Get total usage statistics"""
        collection = get_collection(MODEL_USAGE_COLLECTION)
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_requests": {"$sum": "$requests_made"},
                    "total_tokens": {"$sum": "$tokens_used"},
                    "total_cost": {"$sum": "$cost"}
                }
            }
        ]
        result = list(collection.aggregate(pipeline))
        return result[0] if result else {"total_requests": 0, "total_tokens": 0, "total_cost": 0}

# Initialize database
async def init_db():
    """Initialize MongoDB database"""
    await MongoDBManager.init_db()

# Close database connection
async def close_db():
    """Close MongoDB connection"""
    await MongoDBManager.close_connection()
