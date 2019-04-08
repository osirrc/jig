# OSIRRC 2019 Jig

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool))?

Run the `init.sh` script to download + compile `trec_eval` and download the appropriate topics + qrels.

To test the jig with an Anserini image, try:

```
python run.py prepare \
    --repo rclancy/anserini-test --tag latest \
    --collections [name]=[path] [name]=[path] ...
```

then

```
python run.py search \
    --repo rclancy/anserini-test \
    --collection [name] \
    --topic [topic_file_name] \
    --output /path/to/output \
    --qrels $(pwd)/qrels/qrels.robust2004.txt
```

Change:
 - `[name]` and `[path]` to the collection name and path on the host, respectively
 - `/path/to/output` to the desired output directory.
 
The output run files will appear in the argument of `--output`.
Note that all paths have to be absolute (while `topic` is just the name of the file from the `topics` dir).

# Docker Container Contract

Currently we support three hooks: `init`, `index`, and `search` (called in that order). We expect these three executables to be located in the root directory of the container.

Each script is executed with the interpreter determined by the shebang so you can use  `#!/usr/bin/env bash`, `#!/usr/bin/env python3`, etc - just remember to make sure your `Dockerfile` is built with the appropriate base image or the required dependencies installed. 

### init
The purpose of the `init` hook is to do any preperation needed for the run - this could be downloading + compiling code, downloading a pre-built artifact, or downloading external resources (pre-trained models, knowledge graphs, etc.).

The script will be executed as `./init` with no arguments.

### index
The purpose of the `index` hook is to build the indexes required for the run.

Before the hook is run, we will mount the appropriate document collections at `/input/collections/<name>`, so your script should expect the appropriate collections to be mounted there.

The script will be executed as: `./index --collections <name> <name> ...` where...
- `--collections <name> <name> ...` is a space-delimited list of collection names that map into `/input/collections/<name>`

### search
The purpose of the `search` hook is to perform the ad-hoc retreival runs.

The run files are expected to be placed in the `/output` directory such that they can be evaluated externally by `jig` using `trec_eval`.

The script will be executed as `./search --collection <name> --topic <topic> --topic_format <topic_format>` where...
- `--collection <name>` is the name of the collection being run on (same as the `index` script, so you can map back to the location you chose to store the index)
- `--topic <topic>` is the topic file that maps to `/input/topics/<topic>` 
- `--topic_format <topic_format>` is the format of the topic file

## Reference Images

+ Anserini: [[code](https://github.com/osirrc2019/anserini-docker)] [[Docker Hub](https://hub.docker.com/r/rclancy/anserini-test)]
+ Terrier: [[code](https://github.com/osirrc2019/terrier-docker)]
+ PISA: [[code](https://github.com/osirrc2019/pisa-docker)] [[Docker Hub](https://hub.docker.com/r/pisa/pisa-osirrc2019)]

## Notes

Python 3.5 or higher is required to run `jig`.
