from collections import namedtuple
import json
from typing import Callable

from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

ConlluSample = namedtuple("ConlluSample", ["sent_id", "text", "original", "hidden"])

def ornek_cumleler():
    with open("ornek-cumleler.json", "r") as f:
        obj = json.load(f)

    print(obj)

    with open("ornek-cumleler.jsonl", "w") as f:
        for item in obj:
            print(json.dumps(item), file=f)

def find_an_example_and_strip_form(example_id):

    with open("tr_boun-ud-train.conllu.txt", "r", encoding="utf-8") as f, \
         open("tr_boun-ud-train.conllu_hidden.txt", "w", encoding="utf-8") as out_f:
        line = f.readline()
        while line:
            print(line)
            if line.startswith("# text ="):
                print("# text = HIDDEN", file=out_f)
            elif line.startswith("#") or len(line.strip()) == 0:
                print(line.strip(), file=out_f)
            else:
                tokens = line.split("\t")
                tokens[1] = "HIDDEN"
                out_line = "\t".join(tokens)
                print(out_line.strip(), file=out_f)
            line = f.readline()

def create_llm_chain(template):
    chat_lmm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

    llm_chain = LLMChain(
        llm=chat_lmm,
        prompt=PromptTemplate.from_template(template)
    )
    return llm_chain


def read_file_and_take_N_samples(filepath: str, 
                                 sample_creator_function: Callable[[str, int], list], 
                                 n_samples=10) -> list[ConlluSample]:

    samples = sample_creator_function(filepath, n_samples)
    return samples

def experiment01_sample_creator_function(filepath: str, n_samples: int) -> list[ConlluSample]:
    samples = []
    with open(filepath, "r", encoding="utf-8") as f:
        line = f.readline()
        while line:
            print(line.strip())
            if line.startswith("# sent_id ="):
                sent_id = line[len("# sent_id ="):]
                new_sample = [sent_id, "", "", ""]
                out_line = line
                new_sample[2] += line
                new_sample[3] += out_line
            elif line.startswith("# text ="):
                text = line[len("# text ="):]
                new_sample[1] = text
                out_line = "# text = HIDDEN\n"
                new_sample[2] += line
                new_sample[3] += out_line
            elif line.startswith("#"):
                new_sample[2] += line
                new_sample[3] += out_line
            elif len(line.strip()) == 0:
                new_sample_namedtuple = ConlluSample(new_sample[0], 
                                                     new_sample[1], 
                                                     new_sample[2], 
                                                     new_sample[3])
                samples.append(new_sample_namedtuple)
                new_sample = None
            else:
                tokens = line.split("\t")
                tokens[1] = "HIDDEN"
                out_line = "\t".join(tokens)
                new_sample[2] += line
                new_sample[3] += out_line
            line = f.readline()
            if len(samples) == n_samples:
                break
    return samples


def experiment02_sample_creator_function(filepath: str, n_samples: int) -> list:
    """
    task: Enforce LLm to create an output for each word
    """
    samples = experiment01_sample_creator_function(filepath, n_samples)

    return samples


def experiment03_sample_creator_function(filepath: str, n_samples: int) -> list:
    """
    task: Enforce LLm to create an output for each word
    """
    samples = experiment01_sample_creator_function(filepath, n_samples)

    return samples


def experiment04_sample_creator_function(filepath: str, n_samples: int) -> list:
    """
    task: Enforce LLm to create an output for each word
    """
    samples = experiment01_sample_creator_function(filepath, n_samples)

    return samples


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=["ornek_cumleler", "find_an_example_and_strip_form"], default="find_an_example_and_strip_form")

    args = parser.parse_args()

    if args.command == "find_an_example_and_strip_form":
        find_an_example_and_strip_form(0)
    elif args.command == "ornek_cumleler":
        ornek_cumleler()

if __name__ == "__main__":
    main()