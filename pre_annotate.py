# Local Modules
from formatting import format_unlabelled_data,sent2features,title,line

# Packages
import pickle
import json

def load_crf(filepath):
    with open(filepath,"rb") as f:
        crf = pickle.load(f)
    return crf

def create_annotations(crf,seqs):
    x = [sent2features(s) for s in seqs]
    ner_tags = crf.predict(x)
    return ner_tags

def combine_B_I_tags(seq):
    combi_seq = []
    phrase = ""
    for word,tag in seq:
        if tag == "O":
            if len(phrase)>0:
                combi_seq.append([phrase,phrase_tag])
                phrase = ""
            combi_seq.append([word,tag])
        else:
            if tag[0] == "B":
                if len(phrase)>0:
                    combi_seq.append([phrase,phrase_tag])
                    phrase = ""
                phrase = word
                phrase_tag = tag[2:]
            if tag[0] == "I":
                phrase += " "+word
    if len(phrase)>0:
        combi_seq.append([phrase,phrase_tag])
    return combi_seq

def create_dataset(crf,seqs):
    ner_tags = create_annotations(crf,seqs)
    data = []
    for i in range(len(seqs)):
        data_entry = [[seqs[i][j][0],ner_tags[i][j]] for j in range(len(seqs[i]))]
        data.append(data_entry)
    data = [combine_B_I_tags(seq) for seq in data]
    return data

def get_points(seq):
    start = 0
    end = 0
    starts = []
    ends = []
    for entry in seq:
        starts.append(start)
        start += len(entry[0])+1
        ends.append(start-2)
    new_seq = [[seq[i][0],seq[i][1],starts[i],ends[i]] for i in range(len(seq))]
    return new_seq

def get_annotation(seq,ignore_ents):
    new_seq = get_points(seq)
    annotations = []
    for text,tag,start,end in new_seq:
        if tag not in ignore_ents:
            annot = {}
            annot["label"] = [tag]
            if text[-1] in [",","."]:
                text = text[:-1]
                end -= 1
            annot["points"] = [{"start":start,"end":end,"text":text}]
            annotations.append(annot)
    return annotations

def write_json(file,data,ignore_tags):
    with open(file,"w") as f:
        for seq in data:
            line = {}
            line["content"] = " ".join([i[0] for i in seq])
            line["annotation"]  = get_annotation(seq,ignore_tags)
            line["extras"] = {"Name":"ColumnName","Class":"ColumnValue"}
            f.write(json.dumps(line))
            f.write("\n")
    title(f"Annotations Saved to: {file}")
    return

def pre_annotate_unlabelled(model_path,text_file,save_file,ignore_tags=["O"]):
    '''
    Inputs:
    
    annotated_file - file path to labelled data in .tsv format outputed from dataturks
    
    unannotated_file - file path to .txt file with each line containing an unannotated sentance
    
    save_file - file path to annotations generatated by crf model for upload to dataturks
    
    Outputs:
    
    None
    
    Desc:
    
    Loads annotated data, trains crf model. Makes predictions on unannottated sentances and saves
    output for upload to dataturks annotation service. 
    
    
    '''
    
    _,seqs = format_unlabelled_data(text_file)
    crf = load_crf(model_path)
    data = create_dataset(crf,seqs)
    write_json(save_file,data,ignore_tags)
    print("\nSample Raw Text:")
    print(' '.join([a for a,b in seqs[0]]))
    print("\nSample Prediction:")
    print(data[0])
    print("\n","-"*40)
    return

if __name__ == "__main__":
    crf_path = "./models/crf_Thu_Jan__2_12:54:14_2020"
    unlabelled_file = "./data/unlabelled/sample_unlabelled.txt"
    save_file = "./data/pre_annotated/pre_annotated_sample.txt"
    ignore_tags = ["O",
                "Duration",
                "BODY",
                ]
    title("Testing Pre-Annotation...")
    pre_annotate_unlabelled(crf_path,unlabelled_file,save_file,ignore_tags)