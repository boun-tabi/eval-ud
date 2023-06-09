import time
import experiment04_prompts

from util import create_llm_chain, read_file_and_take_N_samples
from util import experiment04_sample_creator_function


def run_experiment_04(n_samples=1, output_filename="experiment04_output.tsv"):
    """
    run experiment
    """

    llm_chain = create_llm_chain(experiment04_prompts.template)

    results = []
    samples = read_file_and_take_N_samples(
        "tr_boun-ud-train-211.conllu.txt",
        sample_creator_function=experiment04_sample_creator_function,
        n_samples=n_samples
    )
    for sample in samples:
        print(sample.original)
        print(sample.hidden)
        output = perform_a_single_call_04(llm_chain, sample.hidden)
        # output_text = \
        # "\"" + output["text"].replace("\n", "\\n").replace("\t", "\\t") + "\""
        output_text = output["text"]
        results.append((sample.sent_id, output_text, sample.original))
        time.sleep(0.1)

    with open(output_filename, "w", encoding="utf8") as f:
        for result in results:
            print("\n----\n".join(x.strip() for x in list(result) + ["========================"]), file=f)
    print(results)


def perform_a_single_call_04(llm_chain, test_input):
    """"
    This function
    """
    output = llm_chain({
        "example_input": experiment04_prompts.example_input,
        "example_output": experiment04_prompts.example_output, 
        "test_input": test_input
    })
    print(output)
    print(output["text"])
    return output