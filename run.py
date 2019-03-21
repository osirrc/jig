import argparse
import os
import subprocess

import docker

TOPIC_PATH_HOST = os.path.join(os.getcwd(), "topics")
TOPIC_PATH_GUEST = "/input/topics/"

COLLECTION_PATH_GUEST = "/input/collections/"
OUTPUT_PATH_GUEST = "/output"


def build_image():
    base = client.containers.run("{}:{}".format(args.repo, args.tag), command="sh -c '/init; /index {}'".format(args.collection_name), volumes=volumes, detach=True)
    base.wait()
    base.commit(repository=args.repo, tag="save")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=str, help="the image repo (i.e., anserini)")
    parser.add_argument("--tag", required=True, type=str, help="the image tag (i.e., latest)")
    parser.add_argument("--collection_name", required=True, type=str, help="the name of the collection")
    parser.add_argument("--collection_path", required=True, type=str, help="the path of the collection on the host")
    parser.add_argument("--output", required=True, type=str, help="the output directory for run files on the host")
    parser.add_argument("--topic", required=True, type=str, help="the topic file for search")
    parser.add_argument("--topic_format", default="TREC", type=str, help="the topic file for search")
    parser.add_argument("--qrels", required=True, type=str, help="the qrels file for evaluation")
    parser.add_argument("--build", default=False, type=bool, help="whether we re-build the image from scratch")

    # Parse the args
    args = parser.parse_args()

    # Create Docker client
    client = docker.from_env()

    volumes = {
        args.collection_path: {
            "bind": os.path.join(COLLECTION_PATH_GUEST, args.collection_name),
            "mode": "ro"
        },
        args.output: {
            "bind": OUTPUT_PATH_GUEST,
            "mode": "rw"
        },
        TOPIC_PATH_HOST: {
            "bind": TOPIC_PATH_GUEST,
            "mode": "ro"
        },
    }

    exists = len(client.images.list(filters={"reference": "{}:{}".format(args.repo, "save")}))

    if not exists or args.build:
        print("Not existing image found, building image...")
        build_image()

    print("Starting container from existing image...")
    container = client.containers.run("{}:{}".format(args.repo, "save"), command="sh -c '/search {} {}'".format(args.topic, args.topic_format), volumes=volumes, detach=True)
    container.wait()

    print("Evaluating results using trec_eval...")
    for file in os.listdir(args.output):
        run = os.path.join(args.output, file)
        print("###\n# {}\n###".format(run))
        subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", args.qrels, run])
        print()
