import re, json, argparse
from pathlib import Path

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--docs', type=str, required=True)
    parser.add_argument('-l', '--lang', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    return parser.parse_args()

def main():
    args = get_args()
    lang = args.lang

    home_dir = Path.home()
    docs_dir = Path(args.docs)
    lang_dir = docs_dir / '_{}'.format(lang)
    pos_lang_dir = lang_dir / 'pos'
    pos_lang_files = [f for f in pos_lang_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']
    dep_lang_dir = lang_dir / 'dep'
    dep_lang_files = [f for f in dep_lang_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']
    feat_lang_dir = lang_dir / 'feat'
    feat_lang_files = [f for f in feat_lang_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']
    pos_u_dir = docs_dir / '_u-pos'
    pos_u_files = [f for f in pos_u_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']
    dep_u_dir = docs_dir / '_u-dep'
    dep_u_files = [f for f in dep_u_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']
    feat_u_dir = docs_dir / '_u-feat'
    feat_u_files = [f for f in feat_u_dir.iterdir() if f.suffix == '.md' and f.name != 'README.md' and f.name != 'index.md']

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
    title_pattern = re.compile(r'^title:(.*?)$', re.MULTILINE)
    shortdef_pattern = re.compile(r'^shortdef *:(.*?)$', re.MULTILINE)
    for f in pos_lang_files + pos_u_files + dep_lang_files + dep_u_files + feat_lang_files + feat_u_files:
        with open(f, 'r', encoding='utf-8') as fin:
            content = fin.read()
        lines = content.split('\n')
        title, shortdef, rem_content = None, None, None
        three_dash_count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            title_search = title_pattern.search(line)
            if title_search:
                title = title_search.group(1).strip()
                if apos_pattern.match(title):
                    title = title[1:-1]
            shortdef_search = shortdef_pattern.search(line)
            if shortdef_search:
                shortdef = shortdef_search.group(1).strip()
                if apos_pattern.match(shortdef):
                    shortdef = shortdef[1:-1]
            if three_dash_count >= 2:
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
            if line.strip() == '---':
                three_dash_count += 1
        if (f'_{lang}/pos/' in str(f) or '_u-pos/' in str(f)) and title not in pos_d:
            pos_d[title] = {'shortdef': shortdef, 'content': rem_content}
        elif (f'_{lang}/dep/' in str(f) or '_u-dep/' in str(f)) and title not in dep_d:
            dep_d[title] = {'shortdef': shortdef, 'content': rem_content}
        elif (f'_{lang}/feat/' in str(f) or '_u-feat/' in str(f)) and title not in feat_d:
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

    output_path = Path(args.output)
    pos_output = output_path / f'pos-{lang}.json'
    with open(pos_output, 'w', encoding='utf-8') as fout:
        json.dump(pos_d, fout, indent=2, ensure_ascii=False)
    dep_output = output_path / f'dep-{lang}.json'
    with open(dep_output, 'w', encoding='utf-8') as fout:
        json.dump(dep_d, fout, indent=2, ensure_ascii=False)
    feat_output = output_path / f'feat-{lang}.json'
    with open(feat_output, 'w', encoding='utf-8') as fout:
        json.dump(feat_d, fout, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()