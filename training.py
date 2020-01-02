# Local Modules
from formatting import format_labelled_data,line,title

# Packages
import time
import pickle

from sklearn_crfsuite import CRF
from sklearn.model_selection import cross_val_predict
from seqeval.metrics import f1_score,classification_report
from sklearn.model_selection import train_test_split

def log_results(y_true,y_pred):
    file = "./data/model_results.csv"
    f1 = f1_score(y_true,y_pred)
    with open(file,'a') as f:
        results = f"\n{f1},{len(y_true)},{time.ctime()}"
        f.writelines(results)
    print(f"Results Successfully Saved to: {file}")
    return

def save_crf(crf):
    file = f"./models/crf_{time.ctime().replace(' ','_')}"
    with open(file,'wb') as f:
        pickle.dump(crf,f)
    line(60)
    print(f"Model Successfully Saved as: {file}")
    line(60)
    return 

def train_crf(labelled_files,save=True,eval=True):
    x,y,_ = format_labelled_data(labelled_files)
    
    crf = CRF(algorithm='lbfgs',
          c1=0.1,
          c2=0.1,
          max_iterations=100,
          all_possible_transitions=False)
    
    if eval:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
        crf.fit(x_train,y_train)
        pred = crf.predict(x_test)
        report = classification_report(y_test,pred)
        print("Test Results:\n")
        line(60)
        print(report)
        line(60)
        log_results(y_test,pred)
        line(60)
    
    else:
        crf.fit(x,y)
    
    if save:
        save_crf(crf)

    return crf
    
if __name__ == "__main__":
    labelled_files = ["./data/labelled/sample_labelled.tsv"]
    title("Testing CRF training...")
    crf = train_crf(labelled_files)
