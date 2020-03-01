from google.cloud import secretmanager_v1beta1 as secretmanager
import os
import json
import re
import feedparser
import logging

logger = logging.getLogger("Handler")
level = logging.getLevelName('INFO')
logger.setLevel(level)

RSS_DICT = {
    'tech': 'https://www.google.com/alerts/feeds/01736057707602744226/6181175218216352531',
    'politics' : 'https://www.google.com/alerts/feeds/01736057707602744226/11649100745229852174'
}

class RSSReader:
    def __init__(self, db, topic = 'tech'):
        assert topic in RSS_DICT.keys(), f"Your topic must be one of the following: {RSS_DICT.keys()}."
        self.topic = topic
        self.url = RSS_DICT[topic]
        self.id_regex = re.compile('feed\:(.*)$')
        self.url_regex = re.compile(r'url=(.*)&ct=')
        self.db = db
        logger.info(f'Initialised with topic : {topic}')
    
    def make_request(self):
        logger.info(f'Retrieving RSS feed from {self.url}')
        response = feedparser.parse(self.url)
        entries = response['entries']

        logger.info(f'{len(entries)} were found...')

        data = [self.filter_dict(entry, ['id', 'link', 'title', 'summary' , 'published']) for entry in entries]
        return data

    def filter_dict(self, dirty_dict, keys):
        res = {k:v for k,v in dirty_dict.items() if k in keys}
        res['id'] = self.parse_id(res['id'])
        res['link'] = self.parse_url(res['link'])
        res['topic'] = self.topic
        return res

    def parse_id(self, id_string):
        match = self.id_regex.search(id_string)
        return match[1] if match else id_string

    def parse_url(self, url_string):
        match = self.url_regex.search(url_string)
        return match[1] if match else url_string

    def fetch_and_write(self):
        docs = self.make_request()
        data = [doc for doc in docs if self.db.id_not_exists(doc['id'])]
        self.db.write_many_to_db(data)

class DatabaseAdapter:
    def __init__(self, db_conn, name):
        self.conn = db_conn
        self.name = name
        self.collection = self.conn.get_collection(name)
    
    def write_many_to_db(self, data):
        num_items = len(data)
        logger.info(f'Writing {len(data)} items to the {self.name} collection...')
        if num_items > 0 : self.collection.insert_many(data)

    def id_not_exists(self, id):
        return self.collection.count_documents({'id': id}) == 0

def get_secret():
    client = secretmanager.SecretManagerServiceClient()
    SECRET_VERSION = os.environ['SECRET_VERSION']
    response = client.access_secret_version(SECRET_VERSION)
    payload = response.payload.data.decode('UTF-8')
    return json.loads(payload)