import os, json, argparse, csv
from difflib import SequenceMatcher

def main():

    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('-pl', '--prev-llm', type=str, required=True)
    parser.add_argument('-cl', '--curr-llm', type=str, required=True)
    parser.add_argument('-m', '--manual', type=str, required=True)
    parser.add_argument('-n', '--note', type=str, required=True)
    args = parser.parse_args()

    with open(args.prev_llm, 'r', encoding='utf-8') as f:
        prev_llm = json.load(f)
    original_d = {}
    v2_8_d = {}
    for sent in prev_llm:
        v2_8_d[sent['sent_id']] = sent['output']
        original_d[sent['sent_id']] = sent['text']
    with open(args.curr_llm, 'r', encoding='utf-8') as f:
        curr_llm = json.load(f)
    v2_11_d = {}
    for sent in curr_llm:
        v2_11_d[sent['sent_id']] = sent['output']
    with open(args.manual, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        sent_id_order = header.index('Sentence ID')
        version_order = header.index('Version')
        text_order = header.index('Text')
        manual = [row for row in reader]
    manual_d = {}
    for row in manual:
        sent_id = row[sent_id_order]
        version = row[version_order]
        text = row[text_order]
        if sent_id not in manual_d:
            manual_d[sent_id] = {}
        manual_d[sent_id][version] = text

    v2_8_diff_l, v2_11_diff_l = [], []
    v2_8_manual_ratio_l, v2_8_llm_ratio_l, v2_11_manual_ratio_l, v2_11_llm_ratio_l = [], [], [], []
    for sent in manual_d:
        manual_sent = manual_d[sent]
        v2_8_manual = manual_sent['v2.8'].strip()
        v2_8_llm_output = v2_8_d[sent].strip()
        v2_11_manual = manual_sent['v2.11'].strip()
        v2_11_llm_output = v2_11_d[sent].strip()
        original = original_d[sent].strip()
        v2_8_manual_ratio = SequenceMatcher(None, v2_8_manual, original).ratio()
        v2_8_manual_ratio_l.append(v2_8_manual_ratio)
        v2_8_llm_ratio = SequenceMatcher(None, v2_8_llm_output, original).ratio()
        v2_8_llm_ratio_l.append(v2_8_llm_ratio)
        v2_11_manual_ratio = SequenceMatcher(None, v2_11_manual, original).ratio()
        v2_11_manual_ratio_l.append(v2_11_manual_ratio)
        v2_11_llm_ratio = SequenceMatcher(None, v2_11_llm_output, original).ratio()
        v2_11_llm_ratio_l.append(v2_11_llm_ratio)
        v2_8_diff_l.append(v2_8_manual_ratio - v2_8_llm_ratio)
        v2_11_diff_l.append(v2_11_manual_ratio - v2_11_llm_ratio)
    out_d = {}
    out_d['v2.8'] = sum(v2_8_diff_l) / len(v2_8_diff_l)
    out_d['v2.11'] = sum(v2_11_diff_l) / len(v2_11_diff_l)
    out_d['v2.8 manual'] = sum(v2_8_manual_ratio_l) / len(v2_8_manual_ratio_l)
    out_d['v2.8 LLM'] = sum(v2_8_llm_ratio_l) / len(v2_8_llm_ratio_l)
    out_d['v2.11 manual'] = sum(v2_11_manual_ratio_l) / len(v2_11_manual_ratio_l)
    out_d['v2.11 LLM'] = sum(v2_11_llm_ratio_l) / len(v2_11_llm_ratio_l)
    with open(os.path.join(THIS_DIR, 'manual_LLM_comparison-{}-sequence_matching.json'.format(args.note)), 'w', encoding='utf-8') as f:
        json.dump(out_d, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
