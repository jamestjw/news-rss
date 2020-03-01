import pymongo
import ssl
import re
from helper import get_secret, RSSReader, DatabaseAdapter
import logging

logger = logging.getLogger("Handler")
level = logging.getLevelName('INFO')
logger.setLevel(level)

ssl._create_default_https_context = ssl._create_unverified_context

URL = 'https://gnews.io/api/v3/topics/{}'

secret = get_secret()
DB_URL = f"mongodb+srv://{secret['DB_USER']}:{secret['DB_PW']}@{secret['CLUSTER_NAME']}.gcp.mongodb.net/test?retryWrites=true&w=majority"
DB_CONN = pymongo.MongoClient(DB_URL).get_database(secret['DB_NAME'])

def handler(request, callback):
    for topic in ['news','politics']:
        db = DatabaseAdapter(DB_CONN, name = topic)
        RSSReader(db, topic=topic).fetch_and_write()

