import os

import docker

from preparer import Preparer
from searcher import Searcher

TOPIC_PATH_HOST = os.path.join(os.getcwd(), "topics")
TOPIC_PATH_GUEST = "/input/topics/"

COLLECTION_PATH_GUEST = "/input/collections/"
OUTPUT_PATH_GUEST = "/output"


class Manager:

    def __init__(self):
        self.client = docker.from_env(timeout=86_400)
        self.preparer = Preparer()
        self.searcher = Searcher()

    def set_preparer_config(self, preparer_config):
        self.preparer.set_config(preparer_config)

    def set_searcher_config(self, searcher_config):
        self.searcher.set_config(searcher_config)

    def prepare(self, preparer_config=None):
        if preparer_config:
            self.set_preparer_config(preparer_config)
        self.preparer.prepare(self.client, COLLECTION_PATH_GUEST)

    def search(self, searcher_config=None):
        if searcher_config:
            self.set_searcher_config(searcher_config)
        self.searcher.search(self.client, OUTPUT_PATH_GUEST, TOPIC_PATH_HOST, TOPIC_PATH_GUEST)
