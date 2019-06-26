import json
import os
import re
import subprocess
import sys


class Searcher:

    def __init__(self, searcher_config=None):
        self.config = searcher_config

    def set_config(self, searcher_config):
        self.config = searcher_config

    def search(self, client, output_path_guest, topic_path_guest, test_split_path_guest, generate_save_tag):
        """
        Runs the search and evaluates the results (run files placed into the /output directory) using trec_eval
        """
        save_tag = generate_save_tag(self.config.tag, self.config.load_from_snapshot)

        exists = len(client.images.list(filters={"reference": "{}:{}".format(self.config.repo, save_tag)})) != 0
        if not exists:
            sys.exit("Must prepare image first...")

        topic_path_host = os.path.dirname(os.path.abspath(self.config.topic))

        output_path = os.path.abspath(self.config.output)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        volumes = {
            output_path: {
                "bind": output_path_guest,
                "mode": "rw"
            },
            topic_path_host: {
                "bind": topic_path_guest,
                "mode": "ro"
            }
        }

        if len(self.config.test_split) > 0:
            volumes[os.path.abspath(self.config.test_split)] = {"bind": test_split_path_guest, "mode": "ro"}

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

        # The search command
        command = "sh -c '/search --json {}'"

        if self.config.timings:

            # The search command with timings
            command = "sh -c 'time -p /search --json {}'"

            # Duplicate first query
            single_query_file = ''
            with open(os.path.join(topic_path_host, os.path.basename(self.config.topic)), 'r') as file:
                queries = file.read()
                query_end = queries.find('</top>')
                if query_end == -1:
                    sys.exit('Query format unknown...')
                single_query = queries[:query_end + 6]
                single_query_file = os.path.splitext(os.path.basename(self.config.topic))[0] + '.single.txt'
                out_file = open(os.path.join(topic_path_host, single_query_file), 'w')
                out_file.write(single_query)
                out_file.close()

            # Time empty search
            search_args['topic']['path'] = os.path.join(topic_path_guest, single_query_file)
            container = client.containers.run("{}:{}".format(self.config.repo, save_tag), command.format(json.dumps(json.dumps(search_args))), volumes=volumes,
                                              detach=True)
            load_times = []
            for line in container.logs(stream=True):
                match = re.match('^(real|user|sys)\\s(.*)$', line.decode('utf-8'))
                if match:
                    load_times.append(match)

        # Time actual search
        search_args['topic']['path'] = os.path.join(topic_path_guest, os.path.basename(self.config.topic))
        print("Starting container from saved image...")
        container = client.containers.run("{}:{}".format(self.config.repo, save_tag), command.format(json.dumps(json.dumps(search_args))), volumes=volumes,
                                          detach=True)

        search_times = []
        print("Logs for search in container with ID {}...".format(container.id))
        for line in container.logs(stream=True):
            if self.config.timings:
                match = re.match('^(real|user|sys)\\s(.*)$', line.decode('utf-8'))
                if match:
                    search_times.append(match)
            print(str(line.decode('utf-8')), end="")

        if self.config.timings:
            print()

            print('**********')
            print('Index load timing information')
            print(load_times[0].group(0))
            print(load_times[1].group(0))
            print(load_times[2].group(0))
            print()

            print('**********')
            print('Search timing information')
            print(search_times[0].group(0))
            print(search_times[1].group(0))
            print(search_times[2].group(0))
            print()

            result = []
            for i in range(len(load_times)):
                result.append(float(search_times[i].group(2)) - float(load_times[i].group(2)))
            print('**********')
            print('Search timing less load')
            print('real {:.2f}'.format(result[0]))
            print('user {:.2f}'.format(result[1]))
            print('sys {:.2f}'.format(result[2]))
            print()

        # The measure string passed to trec_eval
        measures = " ".join(map(lambda x: "-m {}".format(x), self.config.measures))

        print("Evaluating results using trec_eval...")
        for file in os.listdir(self.config.output):
            if not file.endswith("trec_eval"):
                run = os.path.join(self.config.output, file)
                print("###\n# {}\n###".format(run))
                try:
                    result = subprocess.check_output("trec_eval/trec_eval {} {} {}".format(measures, self.config.qrels, run).split())
                    print(result.decode("UTF-8"))
                    with open("{}.trec_eval".format(run), "w+") as out:
                        out.write(result.decode("UTF-8"))
                except subprocess.CalledProcessError:
                    print("Unable to evaluate {} - is it a run file?".format(run))
