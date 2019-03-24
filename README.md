# OSIRRC 2019 Jig

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool)?

Run the `init.sh` script to download + compile `trec_eval` and download the appropriate topics + qrels.

To test the jig with an Anserini image, try:

```
python run.py prepare \
    --repo rclancy/anserini-test --tag latest \
    --collection_name robust04 --collection_path /path/to/disk45
```

then

```
python run.py search \
    --repo rclancy/anserini-test \
    --topic topics.robust04.301-450.601-700.txt --output /path/to/output \
    --qrels $(pwd)/qrels/qrels.robust2004.txt
```

Change:
 - `/path/to/disk45/` to the location of the collection
 - `/path/to/output` to the desired output directory.
 
The output run files will appear in the argument of `--output`.
Note that all paths have to be absolute (while `topic` is just the name of the file from the `topics` dir).
