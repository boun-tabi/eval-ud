import time
import experiment02_prompts

from util import create_llm_chain, read_file_and_take_N_samples
from util import experiment02_sample_creator_function

def run_experiment_02(n_samples=1, output_filename="experiment02_output.tsv"):

    llm_chain = create_llm_chain(experiment02_prompts.template)

    results = []
    samples = read_file_and_take_N_samples("tr_boun-ud-train-211.conllu.txt", 
                                           sample_creator_function=experiment02_sample_creator_function,
                                           n_samples=n_samples)
    for sample in samples:
        print(sample.original)
        print(sample.hidden)
        output = perform_a_single_call_02(llm_chain, sample.hidden)
        output_text = output["text"].replace("\n", " || ")
        results.append((sample.sent_id, output_text, sample.text))
        time.sleep(0.1)

    with open(output_filename, "w", encoding="utf8") as f:
        for result in results:
            print("\t".join(x.strip() for x in result), file=f)
    print(results)

def perform_a_single_call_02(llm_chain, test_input):
    output = llm_chain({
        "example_input": experiment02_prompts.example_input,
        "example_output": experiment02_prompts.example_output, 
        "test_input": test_input
    })
    print(output)
    print(output["text"])
    return output