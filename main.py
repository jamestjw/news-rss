import pymongo
import ssl
import re
from helper import get_secret, RSSReader, DatabaseAdapter, TOPICS
import logging

logger = logging.getLogger("Handler")
level = logging.getLevelName('INFO')
logger.setLevel(level)

ssl._create_default_https_context = ssl._create_unverified_context

secret = get_secret()
DB_URL = f"mongodb+srv://{secret['DB_USER']}:{secret['DB_PW']}@{secret['CLUSTER_NAME']}.gcp.mongodb.net/test?retryWrites=true&w=majority"
DB_CONN = pymongo.MongoClient(DB_URL).get_database(secret['DB_NAME'])

def handler(request, callback):
    for topic in TOPICS.keys():
        db = DatabaseAdapter(DB_CONN, col_name = topic)
        RSSReader(db, topic=topic).fetch_and_write()

