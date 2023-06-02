import time
import experiment01_prompts

from util import create_llm_chain, read_file_and_take_N_samples

def run_experiment_01(n_samples=1, output_filename="experiment1_output.tsv"):

    llm_chain = create_llm_chain(experiment01_prompts.template)

    results = []
    samples = read_file_and_take_N_samples("tr_boun-ud-train-211.conllu.txt", n_samples=n_samples)
    for sample in samples:
        print(sample.original)
        print(sample.hidden)
        output = perform_a_single_call_01(llm_chain, sample.hidden)
        results.append((sample.sent_id, output["text"], sample.text))
        time.sleep(0.1)

    with open(output_filename, "w", encoding="utf8") as f:
        for result in results:
            print("\t".join(x.strip() for x in result), file=f)
    print(results)

def perform_a_single_call_01(llm_chain, test_input):
    output = llm_chain({
        "example_input": experiment01_prompts.example_input,
        "example_output": experiment01_prompts.example_output, 
        "test_input": test_input
    })
    print(output)
    print(output["text"])
    return output