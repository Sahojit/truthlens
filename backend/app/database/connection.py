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
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "fakenews")
    logger.info(f"Connecting to MongoDB: {db_name}")
    db_instance.client = AsyncIOMotorClient(uri)
    db_instance.db = db_instance.client[db_name]
    # Verify connection
    await db_instance.client.admin.command("ping")
    logger.info("MongoDB connected successfully.")


async def disconnect_db():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")


def get_db():
    return db_instance.db
