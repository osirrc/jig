import argparse

from manager import Manager

if __name__ == "__main__":
    manager = Manager()

    parser = argparse.ArgumentParser()
    parser_sub = parser.add_subparsers()

    # Specific to prepare
    parser_prepare = parser_sub.add_parser("prepare")
    parser_prepare.set_defaults(run=manager.prepare)
    parser_prepare.add_argument("--repo", required=True, type=str, help="the image repo (i.e., osirrc2019/anserini)")
    parser_prepare.add_argument("--tag", default="latest", type=str, help="the image tag (i.e., latest)")
    parser_prepare.add_argument("--save_id", default="save", type=str, help="the ID of the saved image (to search from)")
    parser_prepare.add_argument("--collections", required=True, nargs="+", help="the name of the collection")
    parser_prepare.add_argument("--opts", nargs="+", default="", type=str, help="the args passed to the index script")

    # Specific to search
    parser_search = parser_sub.add_parser("search")
    parser_search.set_defaults(run=manager.search)
    parser_search.add_argument("--repo", required=True, type=str, help="the image repo (i.e., osirrc2019/anserini)")
    parser_search.add_argument("--tag", default="latest", type=str, help="the image tag (i.e., latest)")
    parser_search.add_argument("--save_id", default="save", type=str, help="the ID of the saved image (to search from)")
    parser_search.add_argument("--collection", required=True, help="the name of the collection")
    parser_search.add_argument("--topic", required=True, type=str, help="the topic file for search")
    parser_search.add_argument("--topic_format", default="trec", type=str, help="the topic file format for search")
    parser_search.add_argument("--top_k", default=1000, type=int, help="the number of results for top-k retrieval")
    parser_search.add_argument("--output", required=True, type=str, help="the output directory for run files on the host")
    parser_search.add_argument("--qrels", required=True, type=str, help="the qrels file for evaluation")
    parser_search.add_argument("--opts", nargs="+", default="", type=str, help="the args passed to the search script")

    # Parse the args
    args = parser.parse_args()

    args.run(args)
