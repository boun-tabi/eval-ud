from datetime import datetime
import os, json, argparse, logging
from templates import get_sentence_prompt
from templates import template_sentence_without_dep as template

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--treebank', type=str)
    parser.add_argument('-r', '--run-dir', type=str)
    parser.add_argument('-s', '--sents', type=str)
    parser.add_argument('-m', '--model', type=str)
    parser.add_argument('-n', '--note', type=str)
    parser.add_argument('-u', '--util-dir', type=str)
    parser.add_argument('-k', '--api-path', type=str)
    return parser.parse_args()

def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), 'run-llm-experiment.log'), format='%(asctime)s %(levelname)s %(name)s %(message)s')
    return logger

def main():
    args = get_args()

    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    logger = get_logger()
    logger.info('Started at {now}'.format(now=now))

    script_path = os.path.abspath(__file__)
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    THIS_DIR = os.path.dirname(script_path)

    if args.run_dir:
        run_dir = args.run_dir
        logger.info('Using run directory {run_dir}'.format(run_dir=run_dir))
        with open(os.path.join(run_dir, 'md.json'), 'r', encoding='utf-8') as f:
            md = json.load(f)
        model = md['model']
        tb_path = md['tb_path']
        sents = md['sents']
        sentence_count = md['sentence_count']
        util_dir = md['util_dir']
        api_path = md['api_path']
    else:
        output_dir = os.path.join(THIS_DIR, 'outputs')
        util_dir = args.util_dir
        if args.model:
            model = args.model
        else:
            logger.info('Please specify a model.')
            exit()
        run_dir = os.path.join(output_dir, '{model}-{now}'.format(model=model, now=now))
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(run_dir, 'script.py'), 'w', encoding='utf-8') as f:
            f.write(script_content)
        if args.treebank:
            tb_path = args.treebank
        else:
            logger.info('Please specify a treebank.')
            exit()
        if args.sents:
            sents_path = args.sents
            with open(sents_path, 'r', encoding='utf-8') as f:
                sents = json.load(f)
            sentence_count = len(sents)
        else:
            logger.info('Please specify a sentence list.')
            exit()
        api_path = args.api_path
        with open(os.path.join(run_dir, 'md.json'), 'w', encoding='utf-8') as f:
            md = {'sentence_count': sentence_count, 'sents': sents, 'model': model, 'now': now, 'run_dir': run_dir, 'tb_path': tb_path, 'util_dir': util_dir, 'script_path': script_path, 'api_path': api_path}
            md['prompt'] = template
            if args.note:
                md['note'] = args.note
            json.dump(md, f, ensure_ascii=False, indent=2)

    data_dir = os.path.join(util_dir, 'ud-docs')
    with open(os.path.join(data_dir, 'pos-tr.json'), 'r', encoding='utf-8') as f:
        pos_d = json.load(f)
    with open(os.path.join(data_dir, 'feat-tr-modified.json'), 'r', encoding='utf-8') as f:
        feat_d = json.load(f)

    if model.startswith('poe'):
        with open(os.path.join(api_path)) as f:
            poe_d = json.load(f)
        api_key = poe_d['token']
        from fastapi_poe.types import ProtocolMessage
        from fastapi_poe.client import get_bot_response
        import asyncio
        async def get_response(prompt, bot_name, api_key):
            message = ProtocolMessage(role='user', content=prompt)
            output = ''
            async for partial in get_bot_response(messages=[message], bot_name=bot_name, api_key=api_key):
                output += partial.text
            return output
    else:
        exit('Unknown model: {model}'.format(model=model))

    with open(tb_path, 'r', encoding='utf-8') as f:
        tb_data = json.load(f)

    out_path = os.path.join(run_dir, 'output.json')
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            output_l = json.load(f)
        done_sents_l = [d['sent_id'] for d in output_l]
    else:
        output_l, done_sents_l = [], []
    run_done = True
    asked_count = 0
    for i, sent_id in enumerate(sents):
        print(i, sent_id)
        output = ''
        if sent_id in done_sents_l:
            continue
        text, table = tb_data[sent_id]['text'], tb_data[sent_id]['table']
        prompt = get_sentence_prompt(template, table, pos_d, feat_d)
        d = {'sent_id': sent_id, 'text': text, 'prompt': prompt}
        if model.startswith('poe'):
            try:
                if model == 'poe_GPT-4':
                    output = asyncio.run(get_response(prompt, 'GPT-4', api_key))
                elif model == 'poe_Llama-2-70b':
                    output = asyncio.run(get_response(prompt, 'Llama-2-70b', api_key))
                elif model == 'poe_Mixtral-8x7B-Chat':
                    output = asyncio.run(get_response(prompt, 'Mixtral-8x7B-Chat', api_key))
            except:
                continue
            d['output'] = output
        else:
            print('Unknown model: {model}'.format(model=model))
            d['output'] = ''
        if d['output'] == '':
            continue
        output_l.append(d)
        asked_count += 1
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(output_l, f, ensure_ascii=False, indent=4)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_l, f, ensure_ascii=False, indent=4)
    print('Asked {count} questions.'.format(count=asked_count))
    output_l_len = len(output_l)
    print('Output length: {len}'.format(len=output_l_len))
    if output_l_len != sentence_count:
        run_done = False
        print('Not all tokens are done.')
    else:
        print('All tokens are done.')
    if run_done:
        print('All done.')
    else:
        print('Not all done.')
        os.system('python3 {script_path} -r {run_dir}'.format(script_path=script_path, run_dir=run_dir))
    logger.info('Ended at {now}'.format(now=datetime.now().strftime('%Y%m%d%H%M%S')))

if __name__ == '__main__':
    main()