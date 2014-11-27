import zlib
from app.robot.fetcher.OriginalFetcher import OriginalFetcher
from app.robot.fetcher.SeleniumFetcher import SeleniumFetcher, logging as logger
from app.robot.fetcher.auth.EnvAuth import EnvAuth

__author__ = 'fernando'

from flask import Flask, request
import logging
try:
    import cPickle as pickle
except:
    import pickle
try:
    from multiprocessing import Lock
except:
    try:
        from threading import Lock as TLock
    except:
        pass

from selenium.webdriver.firefox.webdriver import WebDriver
logger.setLevel("DEBUG")
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
fetcher = OriginalFetcher(EnvAuth("USER_PASSWORD"))
lock = Lock()

@app.before_request
def acquire_lock():
    lock.acquire()

@app.before_request
def fetch():
    data = request.form.to_dict()
    try:
        page_number = int(data.pop("page_number", 1))
        fetcher.fetch(data, page_number)
    except Exception, e:
        logger.exception("Error when fetching page")
        return pickle.dumps(e)

@app.after_request
def release_lock(response):
    lock.release()
    return response

@app.route("/fetch_teams/", methods=["POST"])
def fetch_teams():
    try:
        result = fetcher.fetch_teams()
    except Exception, e:
        logger.exception("Error when fetching teams")
        result = e
    return zlib.compress(pickle.dumps(result))

@app.route("/fetch_semesters/", methods=["POST"])
def fetch_semesters():
    try:
        result = fetcher.fetch_semesters()
    except Exception, e:
        logger.exception("Error when fetching semesters")
        result = e
    return zlib.compress(pickle.dumps(result))

@app.route("/fetch_campi/", methods=["POST"])
def fetch_campi():
    try:
        result = fetcher.fetch_campi()
    except Exception, e:
        logger.exception("Error when fetching campi")
        result = e
    return zlib.compress(pickle.dumps(result))

@app.route("/has_next_page/", methods=["POST"])
def has_next_page():
    try:
        result = fetcher.has_next_page()
    except Exception, e:
        logger.exception("Error when verifying if there is a new page")
        result = e
    return zlib.compress(pickle.dumps(result))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)