import codecs
import sys
from sklearn.metrics import accuracy_score

def read_conllu(in_filename, gold_filename, morp_column):
    data = []
    words = []

    gold_fin = codecs.open(gold_filename, "r", encoding="utf-8")


    with codecs.open(in_filename, "r", encoding="utf-8") as fin:

        for payload, gold_payload in zip(fin.read().strip().split("\n\n"),gold_fin.read().strip().split("\n\n")):

            lines = payload.splitlines()
            gold_lines = gold_payload.splitlines()



            body = [line for line in lines if not line.startswith("#")]
            gold_body = [line for line in gold_lines if not line.startswith("#")]

            for line, gold_line in zip(body,gold_body):

                fields = line.split("\t")
                gold_fields = gold_line.split("\t")

                if "-" not in gold_fields[0]:
                    
                   morp = fields[morp_column]
                   pos = fields[3]
                                

                   data.append(morp)
                    
    return words, data

def calc_acc(gold_labels, pred_labels):

    
    return accuracy_score(gold_labels, pred_labels)


if __name__ == "__main__":
    if len(sys.argv) > 4:
        gold_file = sys.argv[1]
        pred_file = sys.argv[2]
        morp_col_gold = int(sys.argv[3])
        morp_col_pred = int(sys.argv[4])
		
        word_gold, gold_l = read_conllu(gold_file, gold_file, morp_col_gold)
        word_pred, pred_l = read_conllu(pred_file, gold_file, morp_col_pred)

        print("All data: ", len(gold_l))
        acc_score = calc_acc(gold_l, pred_l)
        print('Accuracy: ' + str(acc_score))

        county = 0
        correct_county = 0

        n = 0
        v = 0 
        j = 0 
        d = 0
        p = 0
        fn = 0
        fv = 0
        fj = 0
        fd = 0
        fp = 0
        overall = 0
		
        for word, mixed_g, mixed_p in zip(word_gold, gold_l, pred_l):
                       
            if word == "NOUN":
              n = n + 1
            elif word == "VERB":
              v = v + 1
            elif word == "ADJ":
              j = j + 1
            elif word == "ADV":
              d = d + 1
            elif word == "PRON":
              p = p + 1

            if mixed_g != mixed_p:
               if word == "NOUN":
                 fn = fn + 1
               elif word == "VERB":
                 fv = fv + 1
               elif word == "ADJ":
                 fj = fj + 1
               elif word == "ADV":
                 fd = fd + 1
               elif word == "PRON":
                 fp = fp + 1

               #print(word,mixed_g,mixed_p) 
        print("NOUNS :",n,fn,fn/n)
        print("VERBS :",v,fv,fv/v)
        print("ADJ :",j,fj,fj/j)
        print("ADV :",d,fd,fd/d)
        print("PRONS :",p,fp,fp/p)


    else:
        print('Calculates tagging accuracy for files in conllu format.')
        print('The column for the tag can be specified.')
        print('Usage:\n calc_acc.py [goldfilename] [predictionfilename] [tag_column_gold] [tag_column_pred]')