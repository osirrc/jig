# OSIRRC 2019 Jig

What's a [jig](https://en.wikipedia.org/wiki/Jig_(tool))?

Run the `init.sh` script to download + compile `trec_eval` and download the appropriate qrels.

To test the jig with an Anserini image, try:

```
python run.py --repo rclancy/anserini-test --tag latest --collection_name disk45 \
  --collection_path /tuna1/collections/newswire/disk45/ --output /Users/jimmylin/Dropbox/workspace/jig/anserini-output \
  --topic topics.robust04.301-450.601-700.txt --qrels qrels/qrels.robust2004.txt
```

Change `/tuna1/collections/newswire/disk45/` to the location of the collection.
The output run files will appear in the argument of `--output`.
Note that all paths have to be absolute.
