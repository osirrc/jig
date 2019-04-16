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
        save_tag = generate_save_tag(self.config.tag, self.config.save_id)

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
            "collection": self.config.collection,
            "topic": self.config.topic,
            "topic_format": self.config.topic_format,
            "top_k": self.config.top_k
        }

        print("Starting container from saved image...")
        container = client.containers.run("{}:{}".format(self.config.repo, save_tag),
                                          command="sh -c '/search --json {}'".format(json.dumps(json.dumps(search_args))), volumes=volumes, detach=True)

        print("Waiting for search to finish in container '{}'...".format(container.name))
        container.wait()

        print("Evaluating results using trec_eval...")
        for file in os.listdir(self.config.output):
            run = os.path.join(self.config.output, file)
            print("###\n# {}\n###".format(run))
            subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", self.config.qrels, run])
            print()
