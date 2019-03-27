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
    --output /path/to/output \
    --qrels $(pwd)/qrels/qrels.robust2004.txt
```

Change:
 - `[name]` and `[path]` to the collection name and path on the host, respectively
 - `/path/to/output` to the desired output directory.
 
The output run files will appear in the argument of `--output`.
Note that all paths have to be absolute (while `topic` is just the name of the file from the `topics` dir).
