from nltk import pos_tag

# Formatting Labelled Data
def read_labelled(file):
    with open(file) as f:
        lines = [i.rstrip().split("\t") for i in f.readlines()]
    return lines

def clean_words(word_ents):
    '''removes quote and comma characters from'''
    new_word_ents = []
    for ents in word_ents:
        word = ents[0]
        word = word.replace('"','')
        ents[0] = word
        new_word_ents.append(ents)
    return new_word_ents

def create_seqs(word_ents):
    seqs = []
    seq = []
    for ents in word_ents:
        if len(ents)>1:
            if len(ents[0])>0:
                if ents[0][-1] == ".":
                    seq.append([ents[0][:-1],ents[1]])
                if len(ents[0])>1:
                    seq.append([ents[0].replace(",",""),ents[1]])
                else:
                    seq.append(ents)
        else:
            seqs.append([i for i in seq if len(i[0])>0])
            seq=[]
    return seqs

def clean_tags(word_ents):
    '''adds IOB scheme to tags'''
    new_ents = []
    for i in range(0,len(word_ents)):
        if word_ents[i][1] == "O":
            tag = word_ents[i][1]
        else:
            if not i:
                tag = "B-"+word_ents[i][1]
            else:
                if (word_ents[i][1] != word_ents[i-1][1]):
                    tag = "B-"+word_ents[i][1]
                else:
                    tag = "I-"+word_ents[i][1]

        new_ents.append([word_ents[i][0],tag])
    return new_ents

def add_pos(seqs):
    new_seqs = []
    for sentance in seqs:
        words = [word[0] for word in sentance]
        pos = pos_tag(words)        
        new_seq = [pos[i]+(sentance[i][1],) for i in range(len(sentance))]
        new_seqs.append(new_seq)
    return new_seqs

def word2features(sent, i):
    '''
    
    From:
    https://www.depends-on-the-definition.com/named-entity-recognition-conditional-random-fields-python/
    
    '''
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def format_labelled_data(files):
    seqs = []
    for file in files:
        seqs += read_labelled(file) +[[""]]
    seqs = seqs[:-1]
    seqs = create_seqs(seqs)
    seqs = [clean_tags(ents) for ents in seqs]
    seqs = add_pos(seqs)
    x = [sent2features(s) for s in seqs]
    y = [sent2labels(s) for s in seqs]
    tokens = [sent2tokens(s) for s in seqs]
    return x,y,tokens

# Formatting Unlabelled Data
def read_unlabelled(file):
    with open(file) as f:
            lines = [i.rstrip().split(" ") for i in f.readlines()]
    return lines

def add_pos_unlabelled(seqs):
    new_seqs = []
    for sentance in seqs:
        pos = pos_tag(sentance)        
        new_seqs.append(pos)
    return new_seqs

def remove_null_words(seq):
    return [word for word in seq if len(word)>0]

def format_unlabelled_data(file):
    # Load Data 
    seqs = read_unlabelled(file)
    
    # Remove null words
    seqs = [remove_null_words(seq) for seq in seqs]
    
    # Add CRF Features
    seqs = add_pos_unlabelled(seqs)
    x = [sent2features(s) for s in seqs]
    return x,seqs

def line(l=40):
    return print("-"*l)

def title(text):
    line()
    print(text)
    line()
    return

if __name__ == "__main__":
    labelled_files = ["./data/labelled/sample_labelled.tsv"]
    
    # Test Labelled Data Formatting
    title("Formatting Labelled Data...")
    x,y,tokens = format_labelled_data(labelled_files)
    print("\nText Sample:")
    print(tokens[0])
    print("\nLabel Sample:")
    print(y[0])
    print("\nFirst Word Features:")
    print(x[0][0],"\n")
    
    # Test Unlabelled Data Formatting
    title("Formatting Unlabelled Data...")
    unlabelled_file = "./data/unlabelled/sample_unlabelled.txt"
    x,tokens = format_unlabelled_data(unlabelled_file)
    print("\nText Sample:")
    print(tokens[0])
    print("\nFirst Word Features:")
    print(x[0][0],"\n")
    


