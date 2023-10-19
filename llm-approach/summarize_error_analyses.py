import os, json, argparse

def main():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    files = [i for i in os.listdir(THIS_DIR) if i.startswith('error_analysis-') and i.endswith('-annotation.json')]

    aggregate_d = {'increase': {}, 'decrease': {}}
    for file in files:
        with open(os.path.join(THIS_DIR, file), 'r') as f:
            data = json.load(f)
        feats = data['feats']
        increase_d, decrease_d = feats['increase'], feats['decrease']
        for el in increase_d:
            tup = tuple(el['tuple'])
            if tup not in aggregate_d['increase']:
                aggregate_d['increase'][tup] = el['count']
            else:
                aggregate_d['increase'][tup] += el['count']
        for el in decrease_d:
            tup = tuple(el['tuple'])
            if tup not in aggregate_d['decrease']:
                aggregate_d['decrease'][tup] = el['count']
            else:
                aggregate_d['decrease'][tup] += el['count']
    
    new_d = {'increase': [], 'decrease': []}
    for tup in aggregate_d['increase']:
        count = aggregate_d['increase'][tup]
        if count < 5:
            continue
        op = tup[0]
        feat, prev_feat, new_feat = None, None, None
        if op == 'add' or op == 'remove':
            feat = tup[1]
        elif op == 'change':
            prev_feat, new_feat = tup[1], tup[2]
        d = {'operation': op, 'count': aggregate_d['increase'][tup]}
        if feat:
            d['feat'] = feat
        if prev_feat and new_feat:
            d['prev_feat'] = prev_feat
            d['new_feat'] = new_feat
        new_d['increase'].append(d)
    new_d['increase'] = sorted(new_d['increase'], key=lambda x: x['count'], reverse=True)
    for tup in aggregate_d['decrease']:
        count = aggregate_d['decrease'][tup]
        if count < 5:
            continue
        op = tup[0]
        feat, prev_feat, new_feat = None, None, None
        if op == 'add' or op == 'remove':
            feat = tup[1]
        elif op == 'change':
            prev_feat, new_feat = tup[1], tup[2]
        d = {'operation': op, 'count': aggregate_d['decrease'][tup]}
        if feat:
            d['feat'] = feat
        if prev_feat and new_feat:
            d['prev_feat'] = prev_feat
            d['new_feat'] = new_feat
        new_d['decrease'].append(d)
    new_d['decrease'] = sorted(new_d['decrease'], key=lambda x: x['count'], reverse=True)
    aggregate_d = new_d
    
    with open(os.path.join(THIS_DIR, 'aggregate_error_analysis.json'), 'w') as f:
        json.dump(aggregate_d, f, indent=4)

if __name__ == '__main__':
    main()