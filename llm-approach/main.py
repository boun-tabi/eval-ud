import os

import experiment01
import experiment02
import experiment03
import experiment04

os.environ["OPENAI_API_KEY"] = \
    "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"


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=["run_01", 
                                            "run_02", 
                                            "run_03", 
                                            "run_04"])
    parser.add_argument("--n_samples", type=int, default=1)
    parser.add_argument("--output_filename", default="experiment1_output.tsv")

    args = parser.parse_args()

    if args.command == "run_01":
        experiment01.run_experiment_01(args.n_samples, args.output_filename)
    elif args.command == "run_02":
        experiment02.run_experiment_02(args.n_samples, args.output_filename)
    elif args.command == "run_03":
        experiment03.run_experiment_03(args.n_samples, args.output_filename)
    elif args.command == "run_04":
        experiment04.run_experiment_04(args.n_samples, args.output_filename)


if __name__ == "__main__":
    main()
