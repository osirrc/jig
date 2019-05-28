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

    def search(self, client, output_path_guest, topic_path_host, topic_path_guest,
               test_split_path_guest, generate_save_tag):
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
            }
        }

        if len(self.config.test_split) > 0:
            volumes[os.path.abspath(self.config.test_split)] = {
                "bind": test_split_path_guest, "mode": "ro"}

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
            command = "sh -c 'time /search --json {}'"

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
                match = re.match('^(real|user|sys)\t*(.*)m(\s*)(.*)s$', line.decode('utf-8'))
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
                match = re.match('^(real|user|sys)\t*(.*)m(\s*)(.*)s$', line.decode('utf-8'))
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

            result_minutes = []
            result_seconds = []
            for i in range(len(load_times)):
                result_minutes.append(int(search_times[i].group(2)) - int(load_times[i].group(2)))
                result_seconds.append(float(search_times[i].group(4)) - float(load_times[i].group(4)))
            print('**********')
            print('Search timing less load')
            print('real\t{}m{}{:.3f}s'.format(result_minutes[0], search_times[0].group(3), result_seconds[0]))
            print('user\t{}m{}{:.3f}s'.format(result_minutes[1], search_times[0].group(3), result_seconds[1]))
            print('sys\t{}m{}{:.3f}s'.format(result_minutes[2], search_times[0].group(3), result_seconds[2]))
            print()

        print("Evaluating results using trec_eval...")
        for file in os.listdir(self.config.output):
            run = os.path.join(self.config.output, file)
            print("###\n# {}\n###".format(run))
            subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", self.config.qrels, run])
            print()
