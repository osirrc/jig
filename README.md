# OSIRRC 2019 Jig

This is the jig for the [SIGIR 2019 Open-Source IR Replicability Challenge (OSIRRC 2019)](https://osirrc.github.io/osirrc2019/). Check out the [OSIRRC 2019 image library](https://github.com/osirrc/osirrc2019-library) for a list of images that have been contributed to this exercise.

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool))?


To get started, clone the jig, and then download + compile `trec_eval` with the following command:

```
git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval
```

Make sure the Docker Python package is installed (via pip, conda, etc.):
```
pip install -r requirements.txt
```

Make sure the Docker daemon is running.

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
    --topic /path/to/topic \
    --output /path/to/output \
    --qrels /path/to/qrels
```

Change:
 - `[name]` and `[path]` to the collection name and path on the host, respectively
 - `[format]` is one of `trectext`, `trecweb`, `json`, or `warc`
 - `/path/to/topic` to the path of the topic file
 - `/path/to/output` to the desired output directory.
 - `/path/to/qrels` to the path of appropriate qrels file
 
The output run files will appear in the argument of `--output`.
The full command line parameters are below.

To run a container (from a saved image) that you can interact with, try:

```
python run.py interact \
    --repo osirrc2019/anserini \
    --tag latest
```

## Collections

The following collections are supported:

|   Name   |                            URL                            |
|:--------:|:---------------------------------------------------------:|
|  core17  |          https://catalog.ldc.upenn.edu/LDC2008T19         |
|  core18  |             https://trec.nist.gov/data/wapost/            |
|   cw09b  |           http://lemurproject.org/clueweb09.php/          |
|   cw12b  | http://lemurproject.org/clueweb12/ClueWeb12-CreateB13.php |
|   gov2   | http://ir.dcs.gla.ac.uk/test_collections/gov2-summary.htm |
| robust04 |           https://trec.nist.gov/data_disks.html           |

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
| `--timings` | `flag` | `false` | `--timings` | print timing info (requires `time` command available in the image)

### Command Line Options - train

`python run.py train <options>`

| Option Name | Type | Default | Example | Description
| --- | --- | --- | --- | ---
| `--repo` | `string` | `none` | `--repo osirrc2019/anserini` | the repo on Docker Hub
| `--tag` | `string` | `latest` | `--tag latest` | the tag on Docker Hub
| `--load_from_snapshot` | `string` | `save` | `--load_from_snapshot robust04-exp1` | used to determine the tag of the snapshotted image to search from
| `--topic` | `string` | `none` | `--topic topics/topics.robust04.301-450.601-700.txt` | the path of the topic file
| `--topic_format` | `string` | `trec` | `--topic_format trec` | the format of the topic file
| `--test_split` | `string` | `none` | `--test_split $(pwd)/sample_training_validation_query_ids/robust04/test.txt` | the path to the file with the query ids to use for testing (the docker image is expected to compute the training topic ids which will include all topic ids excluding the ones passed in the test and validation ids files)
| `--validation_split` | `string` | `none` | `--validation_split $(pwd)/sample_training_validation_query_ids/robust04/validation.txt` | the path to the file with the query ids to use for the model validation (the docker image is expected to compute the training topic ids which will include all topic ids excluding the ones passed in the test and validation ids files)
| `--model_folder` | `string` | `none` | `--model_folder $(pwd)/output` | the folder to save the model trained by the docker
| `--qrels` | `string` | `none` | `--qrels $(pwd)/qrels/qrels.robust2004.txt` | the qrels file for evaluation
| `--opts` | `[key]=[value] ...` | `none` | `--opts epochs=10` | extra options passed to the search script


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
  "opts": { // extra options passed to the init script
      "<key>": "<value>"
   }
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

### train
The purpose of the `train` hook is to train a retrieval model.

The script will be executed as: `./train --json <json> ` where the JSON string has the following format:
```json5
{
  "topic": {
    "path": "/path/to/topic", // the path to the topic file
    "format": "trec"          // the format of the topic file
  },
  "qrels": {
    "path": "/path/to/qrel",  // the path to the qrel file
  },
  "model_folder": {
    "path": "/output",  // the path (in the docker image) where the output model folder (passed to the jig) is mounted
  },
  "opts": { // extra options passed to the train script
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

Note: If you need a port accessible, ensure you `EXPOSE` the port in your `Dockerfile`.

## Azure Script

Run the script as follows:
`./azure.sh --disk-name <disk_name> --resource-group <group> --vm-name <vm_name> --vm-size <vm_size> --run-file <file.json> --ssh-pubkey-path <path> --subscription <id>`

The runs are defined in a JSON file, see `azure.json` as an example. Values in `[]` (i.e., `[COLLECTION_PATH]`) are replaced with the appropriate values defined in the file.

## Notes

Python 3.5 or higher is required to run `jig`.
