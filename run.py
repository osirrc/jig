import argparse
import os
import subprocess
import sys

import docker

from manager import Manager


if __name__ == "__main__":
    manager = Manager()

    parser = argparse.ArgumentParser()
    parser_sub = parser.add_subparsers()

    # Specific to prepare
    parser_prepare = parser_sub.add_parser("prepare")
    parser_prepare.set_defaults(run=manager.prepare)
    parser_prepare.add_argument("--repo", required=True, type=str, help="the image repo (i.e., rclancy/anserini-test)")
    parser_prepare.add_argument("--tag", required=True, type=str, help="the image tag (i.e., latest)")
    parser_prepare.add_argument("--collections", required=True, nargs="+", help="the name of the collection")

    # Specific to search
    parser_search = parser_sub.add_parser("search")
    parser_search.set_defaults(run=manager.search)
    parser_search.add_argument("--repo", required=True, type=str, help="the image repo (i.e., rclancy/anserini-test)")
    parser_search.add_argument("--collection", required=True, help="the name of the collection")
    parser_search.add_argument("--topic", required=True, type=str, help="the topic file for search")
    parser_search.add_argument("--topic_format", default="TREC", type=str, help="the topic file format for search")
    parser_search.add_argument("--output", required=True, type=str, help="the output directory for run files on the host")
    parser_search.add_argument("--qrels", required=True, type=str, help="the qrels file for evaluation")

    # Parse the args
    args = parser.parse_args()

    args.run(args)
