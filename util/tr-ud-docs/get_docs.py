import os, re, json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
home_dir = os.path.expanduser('~')
docs_dir = os.path.join(home_dir, 'repos', 'ud_docs')
tr_dir = os.path.join(docs_dir, '_tr')
pos_tr_dir = os.path.join(tr_dir, 'pos')
pos_tr_files = [os.path.join(pos_tr_dir, f) for f in os.listdir(pos_tr_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']
dep_tr_dir = os.path.join(tr_dir, 'dep')
dep_tr_files = [os.path.join(dep_tr_dir, f) for f in os.listdir(dep_tr_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']
feat_tr_dir = os.path.join(tr_dir, 'feat')
feat_tr_files = [os.path.join(feat_tr_dir, f) for f in os.listdir(feat_tr_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']
# u_dir = os.path.join(docs_dir, '_u')
# pos_u_dir = os.path.join(docs_dir, '_u-pos')
# pos_u_files = [os.path.join(pos_u_dir, f) for f in os.listdir(pos_u_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']
# dep_u_dir = os.path.join(docs_dir, '_u-dep')
# dep_u_files = [os.path.join(dep_u_dir, f) for f in os.listdir(dep_u_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']
# feat_u_dir = os.path.join(docs_dir, '_u-feat')
# feat_u_files = [os.path.join(feat_u_dir, f) for f in os.listdir(feat_u_dir) if f.endswith('.md') and f != 'README.md' and f != 'index.md']

pos_d, dep_d, feat_d = {}, {}, {}
apos_pattern = re.compile(r'^\'.*?\'$')
b_pattern = re.compile(r'<b>(.*?)</b>')
italic1_pattern = re.compile(r'\*(.*?)\*')
italic2_pattern = re.compile(r'_(.*?)_')
heading_pattern = re.compile(r'#+\s+(.*?)')
comments_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
three_newline_pattern = re.compile(r'\n\n\n')
link1_pattern = re.compile(r'\[(.*?)\]\(.*?\)')
feat_pattern = re.compile(r'^<a name=".+?">(.+?)</a>:(.+?)$')
code_pattern = re.compile(r'`(.*?)`')
sdparse_pattern = re.compile(r'~~~ sdparse(.*?)~~~', re.DOTALL)
# for f in pos_tr_files + pos_u_files + dep_tr_files + dep_u_files + feat_tr_files + feat_u_files:
for f in pos_tr_files + dep_tr_files + feat_tr_files:
    with open(f, 'r', encoding='utf-8') as fin:
        content = fin.read()
        lines = content.split('\n')
        title, shortdef, rem_content = None, None, None
        three_dash_count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if three_dash_count == 1:
                if line.startswith('title:'):
                    title = line.split(':')[1].strip()
                    if apos_pattern.match(title):
                        title = title[1:-1]
                if line.startswith('shortdef:'):
                    shortdef = line.split(':')[1].strip().replace('\'', '')
                    if apos_pattern.match(shortdef):
                        shortdef = shortdef[1:-1]
            elif three_dash_count >= 2:
                rem_lines = lines[i:]
                rem_content = '\n'.join(rem_lines)
                rem_content = b_pattern.sub(r'\1', rem_content)
                rem_content = italic1_pattern.sub(r'\1', rem_content)
                rem_content = italic2_pattern.sub(r'\1', rem_content)
                rem_content = heading_pattern.sub(r'\1', rem_content)
                rem_content = comments_pattern.sub('', rem_content)
                rem_content = link1_pattern.sub(r'\1', rem_content)
                rem_content = code_pattern.sub(r'\1', rem_content)
                rem_content = sdparse_pattern.sub(r'\1', rem_content)
                while three_newline_pattern.search(rem_content):
                    rem_content = three_newline_pattern.sub('\n\n', rem_content)
                rem_content = rem_content.strip()
                break
            if line.startswith('---'):
                three_dash_count += 1
        if '/pos/' in f and title not in pos_d:
            pos_d[title] = {'shortdef': shortdef, 'content': rem_content}
        elif '/dep/' in f and title not in dep_d:
            dep_d[title] = {'shortdef': shortdef, 'content': rem_content}
        elif '/feat/' in f and title not in feat_d:
            lines = rem_content.split('\n')
            feat_d[title] = {'shortdef': shortdef}
            general_content = ''
            current_tag = None
            for line in lines:
                feat_search = feat_pattern.search(line)
                if feat_search:
                    current_tag = feat_search.group(1)
                    feat_d[title][current_tag] = {'shortdef': feat_search.group(2).strip(), 'content': ''}
                elif not current_tag:
                    general_content += line + '\n'
                else:
                    feat_d[title][current_tag]['content'] += line + '\n'
            for tag in feat_d[title]:
                if tag == 'shortdef':
                    continue
                feat_d[title][tag]['content'] = feat_d[title][tag]['content'].strip()
            feat_d[title]['content'] = general_content.strip()

with open(os.path.join(THIS_DIR, 'tr_pos.json'), 'w', encoding='utf-8') as fout:
    json.dump(pos_d, fout, indent=2, ensure_ascii=False)
with open(os.path.join(THIS_DIR, 'tr_dep.json'), 'w', encoding='utf-8') as fout:
    json.dump(dep_d, fout, indent=2, ensure_ascii=False)
with open(os.path.join(THIS_DIR, 'tr_feat.json'), 'w', encoding='utf-8') as fout:
    json.dump(feat_d, fout, indent=2, ensure_ascii=False)