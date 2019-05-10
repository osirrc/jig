import json
import os
import subprocess
import sys


class Searcher:

    def __init__(self, searcher_config=None):
        self.config = searcher_config

    def set_config(self, searcher_config):
        self.config = searcher_config

    def search(self, client, output_path_guest, topic_path_host, topic_path_guest, generate_save_tag):
        """
        Runs the search and evaluates the results (run files placed into the /output directory) using trec_eval
        """
        save_tag = generate_save_tag(self.config.tag, self.config.load_from_snapshot)

        exists = len(client.images.list(filters={"reference": "{}:{}".format(self.config.repo, save_tag)})) != 0
        if not exists:
            sys.exit("Must prepare image first...")

        volumes = {
            os.path.abspath(self.config.output): {
                "bind": output_path_guest,
                "mode": "rw"
            },
            os.path.abspath(topic_path_host): {
                "bind": topic_path_guest,
                "mode": "ro"
            },
        }

        search_args = {
            "collection": {
                "name": self.config.collection
            },
            "opts": {key: value for (key, value) in map(lambda x: x.split("="), self.config.opts)},
            "topic": {
                "path": os.path.join(topic_path_guest, os.path.basename(self.config.topic)),
                "format": self.config.topic_format
            },
            "top_k": self.config.top_k
        }

        print("Starting container from saved image...")
        container = client.containers.run("{}:{}".format(self.config.repo, save_tag),
                                          command="sh -c '/search --json {}'".format(json.dumps(json.dumps(search_args))), volumes=volumes, detach=True)

        print("Logs for search in container with ID {}...".format(container.id))
        for line in container.logs(stream=True):
            print(str(line.decode('utf-8')), end="")

        print("Evaluating results using trec_eval...")
        for file in os.listdir(self.config.output):
            run = os.path.join(self.config.output, file)
            print("###\n# {}\n###".format(run))
            subprocess.run(
                "trec_eval/trec_eval {} {} {}".format(" ".join(map(lambda x: "-m {}".format(x), self.config.measures)), self.config.qrels, run).split())
            print()
