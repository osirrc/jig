import argparse
import os
import subprocess

import docker


def build_image():
    base = client.containers.run("{}:{}".format(args.repo, args.tag), command="sh -c '/init; /index'", volumes=volumes, detach=True)
    base.wait()
    base.commit(repository=args.repo, tag="save")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=str, help="the image repo (i.e., anserini)")
    parser.add_argument("--tag", required=True, type=str, help="the image tag (i.e., latest)")
    parser.add_argument("--collection", required=True, type=str, help="the path of the collection on the host")
    parser.add_argument("--output", required=True, type=str, help="the output directory for run files on the host")
    parser.add_argument("--qrels", required=True, type=str, help="the qrels file for evaluation")
    parser.add_argument("--build", default=False, type=bool, help="whether we re-build the image from scratch")

    # Parse the args
    args = parser.parse_args()

    # Create Docker client
    client = docker.from_env()

    volumes = {
        args.collection: {
            "bind": "/input",
            "mode": "ro"
        },
        args.output: {
            "bind": "/output",
            "mode": "rw"
        },
    }

    exists = len(client.images.list(filters={"reference": "{}:{}".format(args.repo, "save")}))

    if not exists or args.build:
        print("Building image...")
        build_image()

    print("Starting container...")
    container = client.containers.run("{}:{}".format(args.repo, "save"), command="sh -c '/search'", volumes=volumes, detach=True)
    container.wait()

    print("Evaluating...")
    for file in os.listdir(args.output):
        run = os.path.join(args.output, file)
        print("-> {}".format(run))
        subprocess.run(["trec_eval/trec_eval", "-m", "map", "-m", "P.30", args.qrels, run])
