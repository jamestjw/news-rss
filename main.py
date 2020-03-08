import pymongo
import ssl
import re
from helper import get_secret, RSSReader, DatabaseAdapter, TOPICS
import logging
import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

logger = logging.getLogger("Handler")
level = logging.getLevelName('INFO')
logger.setLevel(level)

ssl._create_default_https_context = ssl._create_unverified_context

### test
THRESHOLD = 0.7 
def accept_elem(elem, parent_len):
    text_len = len(elem.text)
    if text_len/parent_len < THRESHOLD:
        return None 
    elems = elem.find_elements_by_xpath("*")
    for e in elems:
        res = accept_elem(e, text_len)
        if res is not None:
            return res
    return elem

###

def readRSS(request, callback):
    driver = webdriver.Chrome(chrome_options = chrome_options)
    driver.get('https://www.indulgexpress.com/car-bike/cars/2020/mar/01/valiant-steed-land-rover-indias-refined-take-on-discovery-sport-promises-added-versatility-22749.html')
    elem = driver.find_element_by_tag_name('body')
    text_len = len(elem.text)

    best_elem = accept_elem(elem, text_len)
    logger.info(best_elem.text)
    logger.info('success')

    ENV = os.environ['ENV']
    secret = get_secret()
    DB_URL = f"mongodb+srv://{secret['DB_USER']}:{secret['DB_PW']}@{secret['CLUSTER_NAME']}.gcp.mongodb.net/test?retryWrites=true&w=majority"
    DB_CONN = pymongo.MongoClient(DB_URL).get_database(secret['DB_NAME'])

    for topic in TOPICS.keys(): 
        db = DatabaseAdapter(DB_CONN, col_name = '_'.join([ENV,topic]))
        RSSReader(db, topic=topic).fetch_and_write()

