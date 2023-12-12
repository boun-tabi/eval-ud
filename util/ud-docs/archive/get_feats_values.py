import requests as r
from bs4 import BeautifulSoup as bs
import json, os, re

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(THIS_DIR, '../../data')
tr_base_url = 'https://universaldependencies.org/tr/feat/{feat_tag}.html'
u_base_url = 'https://universaldependencies.org/u/feat/{feat_tag}.html'
with open(os.path.join(data_dir, 'tr_feats_tags.json'), 'r') as f:
    feat_l = json.load(f)
tag_value_d = {}
for feat in feat_l:
    url = tr_base_url.format(feat_tag=feat)
    page = r.get(url)
    if page.status_code != 200:
        url = u_base_url.format(feat_tag=feat)
        page = r.get(url)
    soup = bs(page.content, 'html.parser')
    h2 = soup.find('h2')
    h2.find('code').decompose()
    h2_text = h2.text[2:]
    tag_value_d[feat] = {'phrase': h2_text, 'values': {}}
    h3_l = soup.find_all('h3')
    for h3 in h3_l:
        code = h3.find('code')
        if code is None:
            continue
        value = code.text
        h3.find('a').decompose()
        h3_text = h3.text[2:]
        value_phrase = h3_text
        tag_value_d[feat]['values'][value] = value_phrase

with open(os.path.join(data_dir, 'tr_feats_values.json'), 'w') as f:
    json.dump(tag_value_d, f, ensure_ascii=False, indent=2)