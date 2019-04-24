# OSIRRC 2019 Jig

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool))?

To get started, download + compile `trec_eval` with the following:

```
git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval
```

For common test collections, [topics](topics/) and [qrels](qrels/) are already checked into this repo.

To test the jig with an Anserini image using default parameters, try:

```
python run.py prepare \
    --repo osirrc2019/anserini \
    --collections [name]=[path]=[format] ...
```

then

```
python run.py search \
    --repo osirrc2019/anserini \
    --collection [name] \
    --topic topics/[topic] \
    --output /path/to/output \
    --qrels qrels/[qrels]
```

Change:
 - `[name]` and `[path]` to the collection name and path on the host, respectively
 - `[format]` is one of `trectext`, `trecweb`, `json`, or `warc`
 - `[topic]` to the path of the topic file
 - `/path/to/output` to the desired output directory.
 - `[qrels]` to the appropriate qrels file
 
The output run files will appear in the argument of `--output`.
The full command line parameters are below.

To run a container (from a saved image) that you can interact with, try:

```
python run.py interact \
    --repo osirrc2019/anserini \
    --tag latest
```

## Command Line Options

Options with `none` as the default are required.

### Command Line Options - prepare

`python run.py prepare <options>`

| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--tag latest` | the tag on Docker Hub
| `--collections` | `[name]=[path]=[format] ...` | `none` | `--collections robust04=/path/to/robust04=trectext ...` | the collections to index
| `--save_to_snapshot` | `string` | `save` | `--save_to_snapshot robust04-exp1` | used to determine the tag of the snapshotted image after indexing
| `--opts` | `[key]=[value] ...` | `none` | `--opts index_args="-storeRawDocs"` | extra options passed to the index script
| `--version` | `string` | `none` | `--version 3b16584a7e3e7e3b93642a95675fc38396581bdf` | the version string passed to the init script

### Command Line Options - search

`python run.py search <options>`

| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--tag latest` | the tag on Docker Hub
| `--collection` | `string` | `none` | `--collection robust04` | the collections to index
| `--load_from_snapshot` | `string` | `save` | `--load_from_snapshot robust04-exp1` | used to determine the tag of the snapshotted image to search from
| `--topic` | `string` | `none` | `--topic topics/topics.robust04.301-450.601-700.txt` | the path of the topic file
| `--topic_format` | `string` | `trec` | `--topic_format trec` | the format of the topic file
| `--top_k` | `int` | `1000` | `--top_k 500` | the number of results for top-k retrieval
| `--output` | `string` | `none` | `--output $(pwd)/output` | the output path for run files
| `--qrels` | `string` | `none` | `--qrels $(pwd)/qrels/qrels.robust2004.txt` | the qrels file for evaluation
| `--opts` | `[key]=[value] ...` | `none` | `--opts search_args="-bm25"` | extra options passed to the search script

### Command Line Options - interact
| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--tag latest` | the tag on Docker Hub
| `--load_from_snapshot` | `string` | `save` | `--load_from_snapshot robust04-exp1` | used to determine the tag of the snapshotted image to interact with
| `--exit_jig` | `string` | `false` | `true` | determines whether jig exits after starting the container
| `--opts` | `[key]=[value] ...` | `none` | `--opts interact_args="localhost:5000"` | extra options passed to the interact script

# Docker Container Contract

Currently we support four hooks: `init`, `index`, `search`,and `interact`. We expect `search` or `interact` to be called after `init` and `index`. We also expect these four executables to be located in the root directory of the container.

Each script is executed with the interpreter determined by the shebang so you can use  `#!/usr/bin/env bash`, `#!/usr/bin/env python3`, etc - just remember to make sure your `Dockerfile` is built with the appropriate base image or the required dependencies are installed. 

### init
The purpose of the `init` hook is to do any preparation needed for the run - this could be downloading + compiling code, downloading a pre-built artifact, or downloading external resources (pre-trained models, knowledge graphs, etc.).

The script will be executed as `./init --json <json>`  where the JSON string has the following format:
```json5
{
  "version": "<version>" // the version string (i.e. commit id, version string, etc.)
}
```

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
  "opts": { // extra options passed to the index script
    "<key>": "<value>"
  },
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
  "opts": { // extra options passed to the search script
    "<key>": "<value>"
  },
  "topic": {
    "path": "/path/to/topic", // the path to the topic file
    "format": "trec"          // the format of the topic file
  },
  "top_k": <int>              // the num of retrieval results for top-k retrieval
}
```

### interact
The purpose of the `interact` hook is to prepare for user interaction, assuming that any process started by `init` or `index` is gone.

The script will be executed as `./interact --json <json>` where the JSON string has the following format:
```json5
{
  "opts": { // extra options passed to the interact script
    "<key>": "<value>"
  },
}
```

## Reference Images

+ Anserini: [[code](https://github.com/osirrc2019/anserini-docker)] [[Docker Hub](https://hub.docker.com/r/rclancy/anserini-test)]
+ Terrier: [[code](https://github.com/osirrc2019/terrier-docker)]
+ PISA: [[code](https://github.com/osirrc2019/pisa-docker)] [[Docker Hub](https://hub.docker.com/r/pisa/pisa-osirrc2019)]

## Notes

Python 3.5 or higher is required to run `jig`.
