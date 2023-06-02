from collections import namedtuple
import os

os.environ["OPENAI_API_KEY"] = "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"

ConlluSample = namedtuple("ConlluSample", ["sent_id", "text", "original", "hidden"])

import experiment01

def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=["run_01"])
    parser.add_argument("--n_samples", type=int, default=1)
    parser.add_argument("--output_filename", default="experiment1_output.tsv")

    args = parser.parse_args()

    if args.command == "run_01":
        experiment01.run_experiment_01(args.n_samples, args.output_filename)

if __name__ == "__main__":
    main()
