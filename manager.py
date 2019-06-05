import hashlib

import docker

from interactor import Interactor
from preparer import Preparer
from searcher import Searcher
from trainer import Trainer

COLLECTION_PATH_GUEST = "/input/collections/"
TOPIC_PATH_GUEST = "/input/topics/"
OUTPUT_PATH_GUEST = "/output"

TEST_SPLIT_PATH_GUEST = '/data/splits/test_split.txt'
VALIDATION_SPLIT_PATH_GUEST = '/data/splits/validation_split.txt'


class Manager:

    def __init__(self):
        self.client = docker.from_env(timeout=86400)
        self.preparer = Preparer()
        self.searcher = Searcher()
        self.trainer = Trainer()
        self.interactor = Interactor()
        self.generate_save_tag = lambda tag, save_id: hashlib.sha256((tag + save_id).encode()).hexdigest()

    def set_preparer_config(self, preparer_config):
        self.preparer.set_config(preparer_config)

    def set_searcher_config(self, searcher_config):
        self.searcher.set_config(searcher_config)

    def set_trainer_config(self, trainer_config):
        self.trainer.set_config(trainer_config)

    def set_interactor_config(self, interactor_config):
        self.interactor.set_config(interactor_config)

    def prepare(self, preparer_config=None):
        if preparer_config:
            self.set_preparer_config(preparer_config)
        self.preparer.prepare(self.client, COLLECTION_PATH_GUEST, self.generate_save_tag)

    def search(self, searcher_config=None):
        if searcher_config:
            self.set_searcher_config(searcher_config)
        self.searcher.search(self.client, OUTPUT_PATH_GUEST, TOPIC_PATH_GUEST, TEST_SPLIT_PATH_GUEST, self.generate_save_tag)

    def train(self, trainer_config=None):
        if trainer_config:
            self.set_trainer_config(trainer_config)
        self.trainer.train(self.client, TOPIC_PATH_GUEST, TEST_SPLIT_PATH_GUEST, VALIDATION_SPLIT_PATH_GUEST, self.generate_save_tag)

    def interact(self, interactor_config=None):
        if interactor_config:
            self.set_interactor_config(interactor_config)
        self.interactor.interact(self.client, self.generate_save_tag)
