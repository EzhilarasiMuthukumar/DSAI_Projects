import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

df = pd.read_csv('spam_ham_dataset.csv')

df = df.dropna(subset=['text', 'label'])
df['text'] = df['text'].str.strip()
df = df[df['text'].str.len() > 20]

spam_samples = df[df['label'] == 'spam'].sample(n=50, random_state=42)
ham_samples = df[df['label'] == 'ham'].sample(n=50, random_state=42)

selected_data = pd.concat([spam_samples, ham_samples]).sample(frac=1, random_state=42).reset_index(drop=True)

texts = selected_data['text'].tolist()
labels = [1 if label == 'spam' else 0 for label in selected_data['label'].tolist()]

train_texts, test_texts, train_labels, test_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
