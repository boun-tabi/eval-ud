import requests as r
from bs4 import BeautifulSoup as bs
import json, os, re

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(THIS_DIR, '../../data')
tr_base_url = 'https://universaldependencies.org/tr/pos/{pos_tag}.html'
u_base_url = 'https://universaldependencies.org/u/pos/{pos_tag}.html'
with open(os.path.join(data_dir, 'tr_pos_tags.json'), 'r') as f:
    pos_l = json.load(f)
tag_value_d = {}
for pos in pos_l:
    url = tr_base_url.format(pos_tag=pos)
    page = r.get(url)
    if page.status_code != 200:
        url = u_base_url.format(pos_tag=pos)
        page = r.get(url)
    soup = bs(page.content, 'html.parser')
    if soup.find('h2') is None:
        pos_ = pos + '_'
        url = tr_base_url.format(pos_tag=pos_)
        page = r.get(url)
        if page.status_code != 200:
            url = u_base_url.format(pos_tag=pos_)
            page = r.get(url)
        soup = bs(page.content, 'html.parser')
    h2 = soup.find('h2')
    h2.find('code').decompose()
    h2_text = h2.text[2:]
    tag_value_d[pos] = h2_text

with open(os.path.join(data_dir, 'tr_pos.json'), 'w') as f:
    json.dump(tag_value_d, f, ensure_ascii=False, indent=2)