import torch
from torch import nn
from torch.utils.data import Dataset
import pandas as pd
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator


class TextClassificationModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_class):
        super(TextClassificationModel, self).__init__()
        self.embedding = nn.EmbeddingBag(vocab_size, embed_dim, sparse=False)
        self.fc = nn.Linear(embed_dim, num_class)
        self.init_weights()

    def init_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()

    def forward(self, text, offsets):
        embedded = self.embedding(text, offsets)
        return self.fc(embedded)


class TextDataset(Dataset):
    def __init__(self, file):
        self.img_labels = pd.read_csv(file, sep='\t')

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        ret = self.img_labels.iloc[idx][0].split(";")[0]
        label = int(self.img_labels.iloc[idx][0].split(";")[1])
        return label, ret


ds1 = TextDataset('train_dataset_extra.csv')
ds2 = TextDataset('train_dataset.csv')
tokenizer = get_tokenizer("basic_english")


def yield_tokens(data_iter):
    for _, text in data_iter:
        yield tokenizer(text)


vocab1 = build_vocab_from_iterator(yield_tokens(ds1), specials=["<unk>"])
vocab1.set_default_index(vocab1["<unk>"])
text_pipeline_extra = lambda x: vocab1(tokenizer(x))

vocab2 = build_vocab_from_iterator(yield_tokens(ds2), specials=["<unk>"])
vocab2.set_default_index(vocab2["<unk>"])
text_pipeline_base = lambda x: vocab2(tokenizer(x))

extra_model = TextClassificationModel(len(vocab1), 64, 2)
base_model = TextClassificationModel(len(vocab2), 60, 67)