import requests as r
from bs4 import BeautifulSoup as bs
import json, os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

base_url = 'https://universaldependencies.org/tr/pos/index.html'
req = r.get(base_url)
soup = bs(req.text, 'html.parser')
table = soup.find('table', {'class': 'typeindex'})
tds = table.find_all('td')
pos_s = set()
for td in tds:
    if td.find('a'):
        pos_s.add(td.find('a').text)
pos_l = sorted(list(pos_s))
data_dir = os.path.join(THIS_DIR, '../../data')
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
with open(os.path.join(data_dir, 'tr_pos_tags.json'), 'w') as f:
    json.dump(pos_l, f, ensure_ascii=False, indent=4)