import numpy as np
import torch
import torch.nn as nn

class QuantumBasedClassifier(nn.Module):
    def __init__(self, vocab_size, num_qubits=24):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, num_qubits)
        self.dropout1 = nn.Dropout(0.25)
        
        self.quantum_layer1 = nn.Parameter(torch.randn(num_qubits, num_qubits) * 0.1)
        self.quantum_layer2 = nn.Parameter(torch.randn(num_qubits, num_qubits) * 0.1)
        self.quantum_layer3 = nn.Parameter(torch.randn(num_qubits, num_qubits) * 0.1)
        
        self.fc1 = nn.Linear(num_qubits, 48)
        self.bn1 = nn.BatchNorm1d(48)
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(48, 24)
        self.bn2 = nn.BatchNorm1d(24)
        self.dropout3 = nn.Dropout(0.15)
        
        self.fc3 = nn.Linear(24, 2)
    
    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)
        x = self.dropout1(x)
        
        x = torch.mm(x, self.quantum_layer1)
        x = torch.tanh(x)
        x = torch.mm(x, self.quantum_layer2)
        x = torch.relu(x)
        x = torch.mm(x, self.quantum_layer3)
        x = torch.sigmoid(x)
        
        x = self.fc1(x)
        x = self.bn1(x)
        x = torch.relu(x)
        x = self.dropout2(x)
        
        x = self.fc2(x)
        x = self.bn2(x)
        x = torch.relu(x)
        x = self.dropout3(x)
        
        x = self.fc3(x)
        return x

def build_vocab(texts):
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for text in texts:
        words = text.lower().replace(',', ' ').replace('.', ' ').split()
        for word in words:
            if word not in vocab and len(word) > 1:
                vocab[word] = len(vocab)
    return vocab

def tokenize_with_vocab(texts, vocab, max_len=30):
    tokenized = []
    for text in texts:
        words = text.lower().replace(',', ' ').replace('.', ' ').split()
        tokens = [vocab.get(word, vocab['<UNK>']) for word in words[:max_len]]
        if len(tokens) < max_len:
            tokens += [vocab['<PAD>']] * (max_len - len(tokens))
        tokenized.append(tokens)
    return torch.LongTensor(tokenized)

def train_quantum(texts, labels, epochs=200):
    torch.manual_seed(42)
    np.random.seed(42)
    
    vocab = build_vocab(texts)
    X = tokenize_with_vocab(texts, vocab)
    y = torch.LongTensor(labels)
    
    torch.manual_seed(42)
    model = QuantumBasedClassifier(len(vocab) + 1)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003, weight_decay=5e-6)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=20)
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        scheduler.step(loss.item())
    
    return model, vocab

def predict_quantum(model, vocab, texts):
    X = tokenize_with_vocab(texts, vocab)
    
    model.eval()
    with torch.no_grad():
        outputs = model(X)
        _, predictions = torch.max(outputs, 1)
    
    return predictions.numpy()
