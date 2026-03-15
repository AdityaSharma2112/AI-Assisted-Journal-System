from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv("MONGO_URL")
client = MongoClient(url)
db = client["arvyax"]
journal_collection = db['journal']