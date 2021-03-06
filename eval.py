# -*- coding: utf-8 -*-
"""eval.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ag2Q2TEpd-P7pVCQcyFpr9VWg1SMyUTc
"""
import argparse
import torch

# from google.colab import drive
# drive.mount('/content/drive')

# !pip install transformers

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', type=str, default='/content/drive/MyDrive/Colab Notebooks/Sentiment Analysis/data', help='directory of csv file')
parser.add_argument('--category', type=str, default='Social', help='category of search')
parser.add_argument('--save_dir', type=str, default='/content/drive/MyDrive/Colab Notebooks/Sentiment Analysis/saved_model', help='directory to save model')
opt = parser.parse_args()
print(opt)

if not torch.cuda.is_available():
    print("WARNING: You have to run with CUDA device")

from transformers import BertTokenizer
from keras.preprocessing.sequence import pad_sequences
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', do_lower_case=False)

def eval_line(line):
    tokenized = [tokenizer.tokenize(word) for word in line]
    token_ids = [tokenizer.convert_tokens_to_ids(token) for token in tokenized]
    token_ids = pad_sequences(token_ids, maxlen=128, dtype="long", truncating="post", padding="post")
    inputs = torch.tensor(token_ids)
    attention_masks=[]
    for sent in token_ids:
        att_mask = [int(token_id > 0) for token_id in sent]
        attention_masks.append(att_mask)
    masks = torch.tensor(attention_masks)
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
    
    with torch.no_grad():
        outputs = model(b_input_ids, 
                token_type_ids=None, 
                attention_mask=b_input_mask)
    logits = outputs[0]
    logits = logits.detach().cpu().numpy()
    return logits

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from transformers import BertForSequenceClassification
# save_dir = '/content/drive/MyDrive/Colab Notebooks/Sentiment Analysis/saved_model'
model = BertForSequenceClassification.from_pretrained(opt.save_dir)
device = "cuda:0"
model = model.to(device)
model.eval()

category = opt.category

date_list = ["2019.12", "2020.01", "2020.02", "2020.03", "2020.04", "2020.05", "2020.06", "2020.07", "2020.08", "2020.09", "2020.10", "2020.11", "2020.12", "2021.01"]
contents = [[] for i in range(len(date_list))]
for i in range(len(date_list)):
    file = pd.read_csv(opt.data_dir + '/' + category + '/' + date_list[i] + '.csv')
    for content in file['title']:
        contents[i].append(content)
sentiments = []
for content in contents:
    pos = 0
    neg = 0
    for line in content:
        logits = eval_line([line])
        if np.argmax(logits):
            pos+=1
        else:
            neg+=1
    sentiments.append(pos / len(content))
    print(date_list[len(sentiments) - 1] + ' : ' + str(sentiments[len(sentiments) - 1]))
print("-------------Finished-------------")
plt.figure(figsize=(15, 8))
plt.plot(date_list, sentiments)
plt.title(category)
plt.show()



