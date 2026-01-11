import torch
import torch.nn as nn
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

class SimpleClassifier(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 16)
        self.fc2 = nn.Linear(16, 2)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def train_classical(texts, labels, epochs=100):
    vectorizer = CountVectorizer(max_features=20)
    X = vectorizer.fit_transform(texts).toarray()
    
    model = SimpleClassifier(X.shape[1])
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.LongTensor(labels)
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
    
    return model, vectorizer

def predict_classical(model, vectorizer, texts):
    X = vectorizer.transform(texts).toarray()
    X_tensor = torch.FloatTensor(X)
    
    with torch.no_grad():
        outputs = model(X_tensor)
        _, predictions = torch.max(outputs, 1)
    
    return predictions.numpy()
