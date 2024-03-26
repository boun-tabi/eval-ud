'''
Running:
```bash
    python3 token-based-task/scripts/create-md_llm-manual.py -c sheets/token.json -l token-based-task/scripts/outputs/poe_GPT-4-2024-02-25_22-41-49 -p1 Akif -p2 Tarık -v1 v2.8 -v2 v2.11 -t token
    python3 token-based-task/scripts/create-md_llm-manual.py -c sheets/token\ with\ dep.json -l token-based-task/scripts/outputs/poe_GPT-4-2024-02-25_22-36-32 -p1 Akif -p2 Tarık -v1 v2.8 -v2 v2.11 -t 'token with dep'
```
'''

import argparse, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    parser.add_argument('-l', '--llm-dir', type=str, required=True)
    parser.add_argument('-p1', '--person1', type=str, required=True)
    parser.add_argument('-p2', '--person2', type=str, required=True)
    parser.add_argument('-v1', '--version1', type=str, required=True)
    parser.add_argument('-v2', '--version2', type=str, required=True)
    parser.add_argument('-t', '--type', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    with open(args.constructions, 'r', encoding='utf-8') as f:
        constructions = json.load(f)
    llm_dir = Path(args.llm_dir)
    version1 = args.version1
    version2 = args.version2
    task_type = args.type
    if task_type == 'token with dep':
        v1_output = llm_dir / '{}_output_dep.json'.format(version1)
        v2_output = llm_dir / '{}_output_dep.json'.format(version2)
    else:
        v1_output = llm_dir / '{}_output.json'.format(version1)
        v2_output = llm_dir / '{}_output.json'.format(version2)
    with open(v1_output, 'r', encoding='utf-8') as f:
        v1_data = json.load(f)
    v1_data_d = {el['q_id']: el for el in v1_data}
    out_d = {el['q_id']: {} for el in v1_data}
    with open(v2_output, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
    v2_data_d = {el['q_id']: el for el in v2_data}
    person1 = args.person1
    person2 = args.person2
    accuracies = { version: { 'manual': { person: [] for person in [person1, person2]}, 'llm': [] } for version in [version1, version2] }
    outputs = { q_id: { version: {} for version in [version1, version2] } for q_id in out_d }
    for q_id in out_d:
        sent_id = v1_data_d[q_id]['sent_id']
        v1_token_id = v1_data_d[q_id]['token_id']
        v2_token_id = v2_data_d[q_id]['token_id']
        original_form = v1_data_d[q_id]['form']
        outputs[q_id]['original_form'] = original_form
        v1_llm_output = v1_data_d[q_id]['output']
        outputs[q_id][version1]['llm'] = v1_llm_output
        if v1_llm_output.lower() == original_form.lower():
            accuracies[version1]['llm'].append(1)
        else:
            accuracies[version1]['llm'].append(0)
        v2_llm_output = v2_data_d[q_id]['output']
        outputs[q_id][version2]['llm'] = v2_llm_output
        if v2_llm_output.lower() == original_form.lower():
            accuracies[version2]['llm'].append(1)
        else:
            accuracies[version2]['llm'].append(0)
        for person in [person1, person2]:
            for version in [version1, version2]:
                if version == version1:
                    person_constructions = constructions[person][version][sent_id][v1_token_id]
                else:
                    person_constructions = constructions[person][version][sent_id][v2_token_id]
                outputs[q_id][version][person] = [i.lower() for i in person_constructions]
                if original_form.lower() in person_constructions:
                    accuracies[version]['manual'][person].append(1)
                else:
                    accuracies[version]['manual'][person].append(0)

    with open(llm_dir / 'outputs.json', 'w', encoding='utf-8') as f:
        json.dump(outputs, f, ensure_ascii=False, indent=2)

    # llm
    v1_llm_accuracy = sum(accuracies[version1]['llm']) / len(accuracies[version1]['llm'])
    accuracies[version1]['llm'] = v1_llm_accuracy
    v2_llm_accuracy = sum(accuracies[version2]['llm']) / len(accuracies[version2]['llm'])
    accuracies[version2]['llm'] = v2_llm_accuracy
    # manual
    v1_manual_person1_accuracy = sum(accuracies[version1]['manual'][person1]) / len(accuracies[version1]['manual'][person1])
    accuracies[version1]['manual'][person1] = v1_manual_person1_accuracy
    v1_manual_person2_accuracy = sum(accuracies[version1]['manual'][person2]) / len(accuracies[version1]['manual'][person2])
    accuracies[version1]['manual'][person2] = v1_manual_person2_accuracy
    v2_manual_person1_accuracy = sum(accuracies[version2]['manual'][person1]) / len(accuracies[version2]['manual'][person1])
    accuracies[version2]['manual'][person1] = v2_manual_person1_accuracy
    v2_manual_person2_accuracy = sum(accuracies[version2]['manual'][person2]) / len(accuracies[version2]['manual'][person2])
    accuracies[version2]['manual'][person2] = v2_manual_person2_accuracy

    with open(llm_dir / 'accuracies.json', 'w', encoding='utf-8') as f:
        json.dump(accuracies, f, ensure_ascii=False, indent=2)
    
    md_str = '| Annotator | {} | {} |\n'.format(version1, version2)
    md_str += '| --- | --- | --- |\n'
    md_str += '| LLM | {:.1f}% | {:.1f}% |\n'.format(v1_llm_accuracy * 100, v2_llm_accuracy * 100)
    md_str += '| {} | {:.1f}% | {:.1f}% |\n'.format(person1, v1_manual_person1_accuracy * 100, v2_manual_person1_accuracy * 100)
    md_str += '| {} | {:.1f}% | {:.1f}% |\n'.format(person2, v1_manual_person2_accuracy * 100, v2_manual_person2_accuracy * 100)
    md_path = llm_dir / 'accuracies.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_str)

if __name__ == '__main__':
    main()