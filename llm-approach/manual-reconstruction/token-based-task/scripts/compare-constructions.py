import argparse, json
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--constructions', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    constructions_path = Path(args.constructions)
    with constructions_path.open('r', encoding='utf-8') as f:
        constructions = json.load(f)
    
    difficulties = ['easy', 'medium', 'difficult', 'random']
    types = ['dep', 'normal']
    versions = ['v1', 'v2']
    annotators = ['Akif', 'Tarık', 'GPT-4']
    scores = {difficulty: {type_t: {version: {annotator: [] for annotator in annotators} for version in versions} for type_t in types} for difficulty in difficulties}
    for difficulty in difficulties:
        for sent_id in constructions[difficulty]:
            for version in constructions[difficulty][sent_id]:
                for token_id in constructions[difficulty][sent_id][version].keys():
                    type_t, form = constructions[difficulty][sent_id][version][token_id]['type'], constructions[difficulty][sent_id][version][token_id]['form']
                    for annotator in annotators:
                        if form == constructions[difficulty][sent_id][version][token_id]['annotators'][annotator]:
                            scores[difficulty][type_t][version][annotator].append(1)
                        else:
                            scores[difficulty][type_t][version][annotator].append(0)
        for type_t in types:
            for version in versions:
                for annotator in annotators:
                    scores[difficulty][type_t][version][annotator] = sum(scores[difficulty][type_t][version][annotator]) / len(scores[difficulty][type_t][version][annotator])
    
    scores['v1_average'] = {type_t: {annotator: 0 for annotator in annotators} for type_t in types}
    for type_t in types:
        for annotator in annotators:
            scores['v1_average'][type_t][annotator] = (scores['easy'][type_t]['v1'][annotator] + scores['medium'][type_t]['v1'][annotator] + scores['difficult'][type_t]['v1'][annotator] + scores['random'][type_t]['v1'][annotator]) / 4
    scores['v2_average'] = {type_t: {annotator: 0 for annotator in annotators} for type_t in types}
    for type_t in types:
        for annotator in annotators:
            scores['v2_average'][type_t][annotator] = (scores['easy'][type_t]['v2'][annotator] + scores['medium'][type_t]['v2'][annotator] + scores['difficult'][type_t]['v2'][annotator] + scores['random'][type_t]['v2'][annotator]) / 4
    
    dir = constructions_path.parent
    scores_path = dir / 'scores.json'
    with scores_path.open('w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)
    
    markdown_str = '# Scores\n\n'
    for type_t in types:
        header_type = 'Dependency' if type_t == 'dep' else 'Normal'
        markdown_str += f'| {header_type} | v2.8 | v2.11 |\n'
        markdown_str += '| --- | --- | --- |\n'
        for annotator in annotators:
            score1, score2 = scores['v1_average'][type_t][annotator] * 100, scores['v2_average'][type_t][annotator] * 100
            markdown_str += f'| {annotator} | {score1:.1f}% | {score2:.1f}% |\n'
        markdown_str += '\n'
    markdown_path = dir / 'scores.md'
    with markdown_path.open('w', encoding='utf-8') as f:
        f.write(markdown_str)

if __name__ == '__main__':
    main()