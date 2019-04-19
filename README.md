# OSIRRC 2019 Jig

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool))?

Run the `init.sh` script to download + compile `trec_eval` and download the appropriate topics + qrels.

To test the jig with an Anserini image, try:

```
python run.py prepare \
    --repo osirrc2019/anserini \
    --tag latest \
    --collections [name]=[path] ...
```

then

```
python run.py search \
    --repo osirrc2019/anserini \
    --tag latest \
    --collection [name] \
    --topic [topic_file_name] \
    --output /path/to/output \
    --qrels $(pwd)/qrels/[qrels]
```

Change:
 - `[name]` and `[path]` to the collection name and path on the host, respectively
 - `[topic_file_name]` to the name of the topic file
 - `/path/to/output` to the desired output directory.
 - `[qrels]` to the appropriate qrels file
 
The output run files will appear in the argument of `--output`.
Note that `topic` is just the name of the file from the `topics` dir.
The full command line parameters are below.

## Command Line Options

Options with `none` as the default are required.

### Command Line Options - prepare

`python run.py prepare <options>`

| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--latest` | the tag on Docker Hub
| `--collections` | `[name]=[path]=[format] ...` | `none` | `--collections robust04=/path/to/robust04=trectext ...` | the collections to index
| `--save_id` | `string` | `save` | `--save_id robust04-exp1` | the ID for intermediate image after indexing
| `--opts` | `[key]=[value] ...` | `none` | `--opts index_args="-storeRawDocs"` | extra options passed to the index script

### Command Line Options - search

`python run.py search <options>`

| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--latest` | the tag on Docker Hub
| `--collection` | `string` | `none` | `--collection robust04` | the collections to index
| `--save_id` | `string` | `save` | `--save_id robust04-exp1` | the ID of the intermediate image
| `--topic` | `string` | `none` | `--topic topics.robust04.301-450.601-700.txt` | the name (not path) of the topic file
| `--top_k` | `int` | `1000` | `--top_k 500` | the number of results for top-k retrieval
| `--output` | `string` | `none` | `--output $(pwd)/output` | the output path for run files
| `--qrels` | `string` | `none` | `--qrels $(pwd)/qrels/qrels.robust2004.txt` | the qrels file for evaluation
| `--opts` | `[key]=[value] ...` | `none` | `--opts search_args="-bm25"` | extra options passed to the search script

# Docker Container Contract

Currently we support three hooks: `init`, `index`, and `search` (called in that order). We expect these three executables to be located in the root directory of the container.

Each script is executed with the interpreter determined by the shebang so you can use  `#!/usr/bin/env bash`, `#!/usr/bin/env python3`, etc - just remember to make sure your `Dockerfile` is built with the appropriate base image or the required dependencies are installed. 

### init
The purpose of the `init` hook is to do any preparation needed for the run - this could be downloading + compiling code, downloading a pre-built artifact, or downloading external resources (pre-trained models, knowledge graphs, etc.).

The script will be executed as `./init` with no arguments.

### index
The purpose of the `index` hook is to build the indexes required for the run.

Before the hook is run, we will mount the document collections at a path passed to the script.

The script will be executed as: `./index --json <json> ` where the JSON string has the following format:

```json5
{
  "collections": [
    {
      "name": "<name>",              // the collection name
      "path": "/path/to/collection", // the collection path
      "format": "<format>"           // the collection format (trectext, trecweb, json, warc)
    },
    ...
  ],
  "opts": [ // extra options passed to the index script
    {
      "key": "<key>",
      "value": "<value>"
    },
    ...
  ]
}
```

### search
The purpose of the `search` hook is to perform an ad-hoc retrieval run - multiple runs can be performed by calling `jig` multiple times with different `--opts` parameters.

The run files are expected to be placed in the `/output` directory such that they can be evaluated externally by `jig` using `trec_eval`.

The script will be executed as `./search --json <json>` where the JSON string has the following format:
```json5
{
  "collection": {
    "name": "<name>"          // the collection name
  },
  "opts": [ // extra options passed to the search script
    {
      "key": "<key>",
      "value": "<value>"
    },
    ...
  ],
  "topic": {
    "path": "/path/to/topic", // the path to the topic file
    "format": "trec"          // the format of the topic file
  },
  "top_k": <int>              // the num of retrieval results for top-k retrieval
}
```

## Reference Images

+ Anserini: [[code](https://github.com/osirrc2019/anserini-docker)] [[Docker Hub](https://hub.docker.com/r/rclancy/anserini-test)]
+ Terrier: [[code](https://github.com/osirrc2019/terrier-docker)]
+ PISA: [[code](https://github.com/osirrc2019/pisa-docker)] [[Docker Hub](https://hub.docker.com/r/pisa/pisa-osirrc2019)]

## Notes

Python 3.5 or higher is required to run `jig`.
