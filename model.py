import argparse
import torch
# -*- coding: utf-8 -*-
"""model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fEGWuPn8_sFCiYk5X_AOjqHrXPOkzpGQ
"""

# from google.colab import drive
# drive.mount('/content/drive')

# !pip install transformers

# !git clone https://github.com/e9t/nsmc.git

parser = argparse.ArgumentParser()
parser.add_argument('--epochs', type=int, default=4, help='number of epochs of training')
parser.add_argument('--save_dir', type=str, default='/content/drive/MyDrive/Colab Notebooks/Sentiment Analysis/saved_model', help='directory to save model')
opt = parser.parse_args()
print(opt)

if not torch.cuda.is_available():
    print("WARNING: You have to run with CUDA device")

import pandas as pd

dTrain = pd.read_csv("nsmc/ratings_train.txt", sep='\t')
dTest = pd.read_csv("nsmc/ratings_test.txt", sep='\t')

dTrain.head(5)

dTest.head(5)

reviews = dTrain['document']
dataset = []
for review in reviews:
    dataset.append("[CLS] " + str(review) + " [SEP]")
dataset[:5]

label = dTrain['label'].values

from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased',do_lower_case=False)

tokenized = [tokenizer.tokenize(data) for data in dataset]

print(dataset[0])
print(tokenized[0])

token_ids = [tokenizer.convert_tokens_to_ids(token) for token in tokenized]

from keras.preprocessing.sequence import pad_sequences
token_ids = pad_sequences(sequences=token_ids, maxlen=128, dtype="long", value=0, truncating="post", padding="post")

token_ids[0]

attention_masks=[]
for sent in token_ids:
    att_mask = [int(token_id > 0) for token_id in sent]
    attention_masks.append(att_mask)
print(attention_masks[0])

from sklearn.model_selection import train_test_split
import torch

train_inputs, validation_inputs, train_labels, validation_labels = train_test_split(token_ids, label, random_state=2018, test_size=0.1)
train_masks, validation_masks, _, _ = train_test_split(attention_masks, label, random_state=2018, test_size=0.1)

train_inputs = torch.tensor(train_inputs)
validation_inputs = torch.tensor(validation_inputs)

train_labels = torch.tensor(train_labels)
validation_labels = torch.tensor(validation_labels)

train_masks = torch.tensor(train_masks)
validation_masks = torch.tensor(validation_masks)

from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler

batch_size = 32

train_data = TensorDataset(train_inputs, train_masks, train_labels)
train_sampler = RandomSampler(train_data)
train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=batch_size)

validation_data = TensorDataset(validation_inputs, validation_masks, validation_labels)
validation_sampler = SequentialSampler(validation_data)
validation_dataloader = DataLoader(validation_data, sampler=validation_sampler, batch_size=batch_size)

from transformers import BertForSequenceClassification, AdamW, BertConfig

model = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels = 2,
    output_attentions = False,
    output_hidden_states = False, 
)

model.cuda()

optimizer = AdamW(model.parameters(),
                  lr = 2e-5,
                  eps = 1e-8 
                )
from transformers import get_linear_schedule_with_warmup
# epochs = 4

total_steps = len(train_dataloader) * opt.epochs

scheduler = get_linear_schedule_with_warmup(optimizer, 
                                            num_warmup_steps = 0, # Default value in run_glue.py
                                            num_training_steps = total_steps)

import numpy as np

def flat_accuracy(preds, labels):
    pred_flat = np.argmax(preds, axis=1).flatten()
    labels_flat = labels.flatten()
    return np.sum(pred_flat == labels_flat) / len(labels_flat)

import time
import datetime
def format_time(elapsed):
    elapsed_rounded = int(round((elapsed)))

    return str(datetime.timedelta(seconds=elapsed_rounded))

device = torch.device("cuda")

import random

seed_val = 42
random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

loss_values = []

for epoch_i in range(0, opt.epochs):
    
    # ========================================
    #               Training
    # ========================================
    
    print("")
    print('======== Epoch {:} / {:} ========'.format(epoch_i + 1, opt.epochs))
    print('Training...')
    t0 = time.time()
    total_loss = 0
    model.train()

    for step, batch in enumerate(train_dataloader):
        if step % 40 == 0 and not step == 0:
            elapsed = format_time(time.time() - t0)
            
            print('  Batch {:>5,}  of  {:>5,}.    Elapsed: {:}.'.format(step, len(train_dataloader), elapsed))

        b_input_ids = batch[0].to(device)
        b_input_mask = batch[1].to(device)
        b_labels = batch[2].to(device)
       
        model.zero_grad()        
       
        outputs = model(b_input_ids, 
                    token_type_ids=None, 
                    attention_mask=b_input_mask, 
                    labels=b_labels)
        
        loss = outputs[0]
        total_loss += loss.item()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_loss / len(train_dataloader)            
    

    loss_values.append(avg_train_loss)
    print("")
    print("  Average training loss: {0:.2f}".format(avg_train_loss))
    print("  Training epcoh took: {:}".format(format_time(time.time() - t0)))
        
    # ========================================
    #               Validation
    # ========================================

    print("")
    print("Running Validation...")
    t0 = time.time()

    model.eval()

    eval_loss, eval_accuracy = 0, 0
    nb_eval_steps, nb_eval_examples = 0, 0

    for batch in validation_dataloader:
        batch = tuple(t.to(device) for t in batch)
        b_input_ids, b_input_mask, b_labels = batch
        
        with torch.no_grad():        
            outputs = model(b_input_ids, 
                            token_type_ids=None, 
                            attention_mask=b_input_mask)
        
        logits = outputs[0]

        logits = logits.detach().cpu().numpy()
        label_ids = b_labels.to('cpu').numpy()
        
        tmp_eval_accuracy = flat_accuracy(logits, label_ids)
        eval_accuracy += tmp_eval_accuracy
        nb_eval_steps += 1

    print("  Accuracy: {0:.2f}".format(eval_accuracy/nb_eval_steps))
    print("  Validation took: {:}".format(format_time(time.time() - t0)))
print("")
print("Training complete!")

# save_dir = '/content/drive/MyDrive/Colab Notebooks/Sentiment Analysis/saved_model'
model.save_pretrained(save_directory=opt.save_dir)

