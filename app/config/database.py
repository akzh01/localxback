from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client.lclx
