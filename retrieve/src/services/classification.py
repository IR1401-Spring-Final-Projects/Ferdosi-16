from sklearn.model_selection import train_test_split
from datasets import Dataset, DatasetDict, load_metric

from transformers import AutoTokenizer, DataCollatorWithPadding, pipeline, \
    AutoModelForSequenceClassification, TrainingArguments, Trainer, AutoConfig

import pandas as pd
import numpy as np
import hazm

import torch.nn as nn
import torch

SAVE_TOTAL_LIMIT = 5

normalizer = hazm.Normalizer(token_based=True)


def get_classifier(checkpoint):
    class Classifier(object):

        def __init__(self):
            config = AutoConfig.from_pretrained(checkpoint)
            self.model = AutoModelForSequenceClassification.from_pretrained(checkpoint, config=config)
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)

        @staticmethod
        def softmax(_outputs):
            maxes = np.max(_outputs, axis=-1, keepdims=True)
            shifted_exp = np.exp(_outputs - maxes)
            return shifted_exp / shifted_exp.sum(axis=-1, keepdims=True)

        def predict(self, text):
            text = normalizer.normalize(text)
            outputs = self.model(**self.tokenizer([text], padding=True, return_tensors='pt'))
            outputs = outputs["logits"][0].detach().numpy()
            outputs = self.softmax(outputs)
            return self.model.config.id2label[outputs.argmax().item()], outputs.max().item()

    return Classifier()


class CustomTrainer(Trainer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{k: v for k, v in kwargs.items()
                                   if k not in {'lose_weight', 'device'}})

        self.wei = kwargs['lose_weight']
        self.dev = kwargs['device']

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get('logits')

        loss_fct = nn.CrossEntropyLoss(
            weight=torch.FloatTensor(self.wei).to(self.dev))

        loss = loss_fct(
            logits.view(-1, self.model.config.num_labels),
            labels.view(-1))

        return (loss, outputs) if return_outputs else loss


class ClassificationModel:

    def __init__(self, model_name, label2id, id2label):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.classifier = None
        self.config = AutoConfig.from_pretrained(model_name, label2id=label2id, id2label=id2label)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, config=self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    @staticmethod
    def training_args_builder(output_dir="../../resources/", learning_rate=2e-5, train_batch_size=16,
                              eval_batch_size=16, num_train_epochs=10, weight_decay=0.01):
        return TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=train_batch_size,
            per_device_eval_batch_size=eval_batch_size,
            weight_decay=weight_decay,
            learning_rate=learning_rate,
            num_train_epochs=num_train_epochs,
            save_steps=100,
            save_total_limit=SAVE_TOTAL_LIMIT,
        )

    def train(self, dataset, lose_weight, training_args=None):
        training_args = training_args or self.training_args_builder()

        train_df, validation_df = train_test_split(dataset, test_size=0.2, random_state=42, shuffle=True)

        train_dataset, validation_dataset = \
            Dataset.from_dict(train_df), Dataset.from_dict(validation_df)

        dataset = DatasetDict({"train": train_dataset, "test": validation_dataset})

        def preprocess_function(data):
            return self.tokenizer(data["text"], truncation=True, padding=True)

        tokenized_data = dataset.map(preprocess_function, batched=True, remove_columns=['text'])

        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)

        CustomTrainer(
            device=self.device,
            lose_weight=lose_weight,
            eval_dataset=tokenized_data["test"],
            train_dataset=tokenized_data["train"],
            model=self.model,
            args=training_args,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
        ).train()

    def predict(self, texts):
        if not self.classifier:
            self.model.to('cpu')
            self.classifier = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)

        inner_labels = self.classifier(texts)
        return list(map(lambda lab: int(lab['label'].split('_')[1]), inner_labels))


if __name__ == '__main__':
    df = pd.read_csv('../../resources/shahnameh-labeled.csv')
    num_stories = 10

    groups = df.groupby('labels').count().sort_values('text', ascending=False)
    groups = groups[:num_stories].reset_index()

    labels = groups.sort_values('labels').labels.tolist()
    counts = groups.sort_values('labels').text.to_numpy()

    id2lab = {idx: label for idx, label in enumerate(labels)}
    lab2id = {label: idx for idx, label in enumerate(labels)}

    df['labels'] = df.labels.apply(lambda x: lab2id.get(x, len(lab2id)))

    df.groupby('labels').count()

    normalizer = hazm.Normalizer(token_based=True)
    df['text'] = df.text.apply(normalizer.normalize)

    main_df, test_df = train_test_split(
        df, test_size=0.1, random_state=42, shuffle=True)

    main_df = main_df[main_df.labels < len(id2lab)]

    weight_loss = (1 / counts) / (1 / counts).sum()

    # New pre-trained model: mitra-mir/BERT-Persian-Poetry
    classifier = ClassificationModel(
        "HooshvareLab/bert-fa-zwnj-base", label2id=lab2id, id2label=id2lab)

    classifier.train(main_df, weight_loss, None)

    predictions = classifier.predict(main_df['text'].to_list())

    print('+ train data:')
    metric = load_metric("f1")
    print("f1_score: ", metric.compute(
        predictions=predictions, references=main_df['labels'], average='micro'))

    metric = load_metric("accuracy")
    print("accuracy: ", metric.compute(
        predictions=predictions, references=main_df['labels']))

    predictions = classifier.predict(test_df['text'].to_list())

    print('+ test data:')
    metric = load_metric("f1")
    print("f1_score: ", metric.compute(
        predictions=predictions, references=test_df['labels'], average='micro'))

    metric = load_metric("accuracy")
    print("accuracy: ", metric.compute(
        predictions=predictions, references=test_df['labels']))
