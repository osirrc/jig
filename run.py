import argparse
import os
import subprocess
import sys

import docker

TOPIC_PATH_HOST = os.path.join(os.getcwd(), "topics")
TOPIC_PATH_GUEST = "/input/topics/"

COLLECTION_PATH_GUEST = "/input/collections/"
OUTPUT_PATH_GUEST = "/output"


def prepare():
    """Builds an image that has been initialized and has indexed the collection.

    The `init` hook is used by the image to perform additional
    initialization tasks (which may be a no-op). The developer is free
    to determine what should be directly baked into the image and what
    should be executed in the init hook.

    The `index` hook is used by the image to index a particular
    collection, which is provided to the script as the first argument
    (`collection_name`). This argument maps into the path
    `/input/collection/collection_name`, where the container can
    expect the document collection to be mounted.
    """
    volumes = {
        args.collection_path: {
            "bind": os.path.join(COLLECTION_PATH_GUEST, args.collection_name),
            "mode": "ro"
        }
    }

    # The first step is to pull an image from an OSIRRC participant,
    # start up a container, run its `init` and `index` hooks, and then
    # use `docker commit` to save the image after the index has been
    # built. The rationale for doing this is that indexing may take a
    # while, but only needs to be done once, so in essence we are
    # "snapshotting" the system with the indexes.
    base = client.containers.run("{}:{}".format(args.repo, args.tag), command="sh -c '/init; /index {}'".format(args.collection_name), volumes=volumes, detach=True)
    base.wait()
    base.commit(repository=args.repo, tag="save")


def search():
    """
    Runs the search and evaluates the results (run files placed into the /output directory) using trec_eval
    """
    exists = len(client.images.list(filters={"reference": "{}:{}".format(args.repo, "save")}))
    if not exists:
        sys.exit("Must prepare image first...")

    volumes = {
        args.output: {
            "bind": OUTPUT_PATH_GUEST,
            "mode": "rw"
        },
        TOPIC_PATH_HOST: {
            "bind": TOPIC_PATH_GUEST,
            "mode": "ro"
        },
    }

    print("Starting container from saved image...")
    container = client.containers.run("{}:{}".format(args.repo, "save"), command="sh -c '/search {} {}'".format(args.topic, args.topic_format), volumes=volumes, detach=True)
    container.wait()

    print("Evaluating results using trec_eval...")
    for file in os.listdir(args.output):
        run = os.path.join(args.output, file)
        print("###\n# {}\n###".format(run))
        subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", args.qrels, run])
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser_sub = parser.add_subparsers()

    # Specific to prepare
    parser_prepare = parser_sub.add_parser("prepare")
    parser_prepare.set_defaults(run=prepare)
    parser_prepare.add_argument("--repo", required=True, type=str, help="the image repo (i.e., rclancy/anserini-test)")
    parser_prepare.add_argument("--tag", required=True, type=str, help="the image tag (i.e., latest)")
    parser_prepare.add_argument("--collection_name", required=True, type=str, help="the name of the collection")
    parser_prepare.add_argument("--collection_path", required=True, type=str, help="the path of the collection on the host")

    # Specific to search
    parser_search = parser_sub.add_parser("search")
    parser_search.set_defaults(run=search)
    parser_search.add_argument("--repo", required=True, type=str, help="the image repo (i.e., rclancy/anserini-test)")
    parser_search.add_argument("--topic", required=True, type=str, help="the topic file for search")
    parser_search.add_argument("--topic_format", default="TREC", type=str, help="the topic file for search")
    parser_search.add_argument("--output", required=True, type=str, help="the output directory for run files on the host")
    parser_search.add_argument("--qrels", required=True, type=str, help="the qrels file for evaluation")

    # Parse the args
    args = parser.parse_args()

    # Create Docker client
    client = docker.from_env()

    # Call the function specified in the set_defaults call for the parser.
    args.run()
