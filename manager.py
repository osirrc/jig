import os
import hashlib

import docker

from preparer import Preparer
from searcher import Searcher
from interactor import Interactor

TOPIC_PATH_HOST = os.path.abspath("topics")
TOPIC_PATH_GUEST = "/input/topics/"

COLLECTION_PATH_GUEST = "/input/collections/"
OUTPUT_PATH_GUEST = "/output"


class Manager:

    def __init__(self):
        self.client = docker.from_env(timeout=400)
        self.preparer = Preparer()
        self.searcher = Searcher()
        self.interactor = Interactor()
        self.generate_save_tag = lambda tag, save_id: hashlib.sha256((tag + save_id).encode()).hexdigest()

    def set_preparer_config(self, preparer_config):
        self.preparer.set_config(preparer_config)

    def set_searcher_config(self, searcher_config):
        self.searcher.set_config(searcher_config)

    def set_interactor_config(self, interactor_config):
        self.interactor.set_config(interactor_config)

    def prepare(self, preparer_config=None):
        if preparer_config:
            self.set_preparer_config(preparer_config)
        self.preparer.prepare(self.client, COLLECTION_PATH_GUEST, OUTPUT_PATH_GUEST, self.generate_save_tag)

    def search(self, searcher_config=None):
        if searcher_config:
            self.set_searcher_config(searcher_config)
        self.searcher.search(self.client, OUTPUT_PATH_GUEST, TOPIC_PATH_HOST, TOPIC_PATH_GUEST, self.generate_save_tag)

    def interact(self, interactor_config=None):
        if interactor_config:
            self.set_interactor_config(interactor_config)
        self.interactor.interact(self.client, self.generate_save_tag)
