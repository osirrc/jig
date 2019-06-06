import json
import os
import sys

QRELS_GUEST_PATH = '/output/qrels/qrels.qrel'
MODELS_GUEST_PATH = '/output'


class Trainer:
    def __init__(self, trainer_config=None):
        self.config = trainer_config

    def set_config(self, trainer_config):
        self.config = trainer_config

    def train(self, client, topic_path_guest, test_split_path_guest,
              validation_split_path_guest, generate_save_tag):
        """
        Performs training
        """
        save_tag = generate_save_tag(self.config.tag, self.config.load_from_snapshot)

        exists = len(client.images.list(filters={"reference": "{}:{}".format(self.config.repo, save_tag)})) != 0
        if not exists:
            sys.exit("Must prepare image first...")

        volumes = {
            os.path.abspath(self.config.model_folder): {
                "bind": MODELS_GUEST_PATH,
                "mode": "rw"
            },
            os.path.abspath(self.config.topic): {
                "bind": os.path.join(topic_path_guest, os.path.basename(self.config.topic)),
                "mode": "ro"
            },
            os.path.abspath(self.config.qrels): {
                "bind": QRELS_GUEST_PATH,
                "mode": "ro"
            },

            os.path.abspath(self.config.test_split): {
                "bind": test_split_path_guest,
                "mode": "ro"
            },
            os.path.abspath(self.config.validation_split): {
                "bind": validation_split_path_guest,
                "mode": "ro"
            }
        }

        train_args = {
            "collection": {
                "name": self.config.collection
            },
            "opts": {key: value for (key, value) in map(lambda x: x.split("="), self.config.opts)},
            "topic": {
                "path": os.path.join(topic_path_guest, os.path.basename(self.config.topic)),
                "format": self.config.topic_format
            },
            "qrels": {
                "path": QRELS_GUEST_PATH
            },
            "model_folder": {
                "path": MODELS_GUEST_PATH
            }
        }

        print("Starting container from saved image...")
        container = client.containers.run("{}:{}".format(self.config.repo, save_tag),
                                          command="sh -c '/train --json {}'".format(json.dumps(json.dumps(train_args))),
                                          volumes=volumes, detach=True)

        print("Logs for training in container with ID {}...".format(container.id))
        for line in container.logs(stream=True):
            print(str(line.decode('utf-8')), end="")
