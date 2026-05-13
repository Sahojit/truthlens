"""
MongoDB Atlas connection management using Motor async driver.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger
import os


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_db():
    uri = os.getenv("MONGODB_URI", "")
    db_name = os.getenv("DATABASE_NAME", "fakenews")
    if not uri:
        logger.warning("MONGODB_URI not set — running without database (predictions work, history disabled).")
        return
    logger.info(f"Connecting to MongoDB: {db_name}")
    try:
        db_instance.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        db_instance.db = db_instance.client[db_name]
        await db_instance.client.admin.command("ping")
        logger.info("MongoDB connected successfully.")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e} — running without database.")


async def disconnect_db():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")


def get_db():
    return db_instance.db
