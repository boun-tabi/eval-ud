import argparse, re, csv
from pathlib import Path
from bs4 import BeautifulSoup

def get_args():
    parser = argparse.ArgumentParser(description='Converts at_glance.html to csv')
    parser.add_argument('-i', '--input', help='Input file', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    input_path = Path(args.input)

    with input_path.open() as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    token_word_sentence_pattern = re.compile(r'(\d+) tokens (\d+) words (\d+) sentences')
    
    accordion_header_l = [div for div in soup.find_all('div', class_='ui-accordion-header ui-helper-reset ui-state-default ui-corner-all', role='tab') if div.find('img', class_='flag')]
    languages = [div.find('span', class_='doublewidespan').text for div in accordion_header_l]
    
    accordion_content_l = soup.find_all('div', class_='ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom', style='', role='tabpanel')
    output_l = []
    for i, accordion_content in enumerate(accordion_content_l):
        language = languages[i]
        treebanks = accordion_content.find_all('div', class_='ui-accordion-header ui-helper-reset ui-state-default ui-corner-all', role='tab')
        for treebank in treebanks:
            treebank_name = treebank.find('span', class_='doublewidespan').text
            treebank_stats = treebank.find('span', class_='widespan').find('span', class_='hint--top hint--info').get('data-hint').replace(',', '')
            tokens, words, sentences = map(int, token_word_sentence_pattern.match(treebank_stats).groups())
            output_l.append([language, treebank_name, tokens, words, sentences])
    
    output_path = input_path.with_suffix('.csv')
    with output_path.open('w') as f:
        writer = csv.writer(f)
        writer.writerow(['Language', 'Treebank Name', 'Token count', 'Word count', 'Sentence count'])
        writer.writerows(output_l)
    
if __name__ == '__main__':
    main()