import subprocess
import os

class Searcher:

    def __init__(self, searcher_config=None):
        self.config = searcher_config
    
    def set_config(self, searcher_config):
        self.config = searcher_config
    
    def search(self, client, output_path_guest, topic_path_host, topic_path_guest):
        """
        Runs the search and evaluates the results (run files placed into the /output directory) using trec_eval
        """
        exists = len(client.images.list(filters={"reference": "{}:{}".format(self.config.repo, "save")})) != 0
        if not exists:
            sys.exit("Must prepare image first...")

        volumes = {
            self.config.output: {
                "bind": output_path_guest,
                "mode": "rw"
            },
            topic_path_host: {
                "bind": topic_path_guest,
                "mode": "ro"
            },
        }

        print("Starting container from saved image...")
        container = client.containers.run("{}:{}".format(self.config.repo, "save"),
                                        command="sh -c '/search --collection {} --topic {} --topic_format {}'".format(
                                            self.config.collection, self.config.topic, self.config.topic_format), volumes=volumes, detach=True)

        print("Waiting for search to finish...")
        container.wait()

        print("Evaluating results using trec_eval...")
        for file in os.listdir(self.config.output):
            run = os.path.join(self.config.output, file)
            print("###\n# {}\n###".format(run))
            subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", self.config.qrels, run])
            print()
