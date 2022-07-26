import logging

from gensim.models import KeyedVectors
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

import hazm
import tqdm
import pandas as pd
import numpy as np
import pickle
import os

from transformers import AutoTokenizer, AutoConfig, AutoModel

logger = logging.getLogger(__name__)
stop_words = set(hazm.stopwords_list() + ['نمی', 'های'])
normalizer = hazm.Normalizer(token_based=True)


def batch_series(iterable, n=2_000):
    length = len(iterable)
    for ndx in range(0, length, n): yield iterable[ndx:min(ndx + n, length)]


class Similarities:

    def __init__(self, dataset, checkpoint=None):

        dataset['text'] = dataset['text'].apply(normalizer.normalize)
        self.dataset = dataset.sort_values('text')
        self.word2vec = KeyedVectors.load_word2vec_format('../../resources/farsi_literature_word2vec_model.txt')

        model_name = 'HooshvareLab/bert-base-parsbert-uncased'
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        self.model = AutoModel.from_pretrained(
            model_name, local_files_only=True, config=AutoConfig.from_pretrained(model_name))

        if checkpoint and os.path.exists(os.path.join(checkpoint, 'pipeline')):

            self.pipe = self.load_model(checkpoint, 'pipeline')
            self.directory = checkpoint

        else:
            logger.warning('It is not possible to load pipeline. Again the models are trained.')

            self.directory = '../../resources/similarities/'
            if not os.path.exists(self.directory): os.mkdir(self.directory)

            self.pipe = Pipeline(
                [('count',
                  CountVectorizer(analyzer='word', ngram_range=(1, 2), max_features=20_000, stop_words=stop_words)),
                 ('tfidf', TfidfTransformer(sublinear_tf=True))]).fit(self.dataset['text'].tolist())

        self.word_idf = dict(zip(self.pipe['count'].get_feature_names_out(), self.pipe['tfidf'].idf_))

        embedders = [
            self.get_tfidf_embeddings,
            self.get_boolean_embeddings,
            self.get_word_cidf_embeddings,
            self.get_transformer_embeddings,
        ]

        for embedder in embedders:

            if any(x.startswith(embedder.__name__[4:]) for x in os.listdir(self.directory)):
                logger.warning(f'Skip {embedder.__name__[4:]}.')
                continue

            for i, batch in tqdm.tqdm(enumerate(batch_series(self.dataset['text'].tolist(), 5_000))):
                embeddings = embedder(batch)
                self.save_model(embeddings, self.directory, f'{embedder.__name__[4:]}.{i}')

        self.save_model(self.pipe, self.directory, 'pipeline')

    @staticmethod
    def get_similar_by_cosine_distance(vector, documents, n=5):
        sq_vector = np.squeeze(vector)
        similarity = documents.dot(sq_vector) / (np.linalg.norm(documents, axis=1) * np.linalg.norm(sq_vector) + 1e-10)
        sorted_idx = np.argsort(similarity)[::-1]

        return sorted_idx[:n], similarity[sorted_idx[:n]]

    @staticmethod
    def save_model(obj, directory, file_name):
        if not os.path.exists(directory):
            os.mkdir(directory)

        pickle.dump(obj, open(os.path.join(directory, file_name), 'wb'))

    @staticmethod
    def load_model(directory, file_name):
        return pickle.load(open(os.path.join(directory, file_name), 'rb'))

    def get_transformer_embeddings(self, documents):

        result = None
        for batch in batch_series(documents, 1_000):
            output = self.model(**self.tokenizer(batch, return_tensors='pt', padding=True))
            output = np.mean(output.last_hidden_state.detach().numpy(), axis=1)
            result = output if result is None else np.concatenate((result, output))

        return result

    def get_word_cidf_embeddings(self, documents):
        def embedder(element, word2vec, word_idf):
            return np.mean(
                [
                    (word2vec[w] if w in word2vec else np.zeros(100)) * word_idf.get(w, 0)
                    for w in hazm.word_tokenize(element)
                ], axis=0).tolist()

        return np.array([embedder(doc, self.word2vec, self.word_idf) for doc in documents])

    def get_tfidf_embeddings(self, documents):
        return self.pipe.transform(documents).toarray()

    def get_boolean_embeddings(self, documents):
        return self.pipe['count'].transform(documents).toarray().astype(bool).astype(int)

    def get_similar_indexes(self, text, n, embedder):
        embedding = embedder([text])
        name = embedder.__name__[4:]

        offset = 0

        indexes, similarities = [], []
        files = filter(lambda file: file.startswith(name), os.listdir(self.directory))
        for file_name in sorted(files):
            batch_embeddings = self.load_model(self.directory, file_name)
            _idx, _sim = self.get_similar_by_cosine_distance(embedding, batch_embeddings, n)

            similarities.extend(_sim)
            indexes.extend(_idx + offset)
            offset = offset + len(batch_embeddings)

        similarities = np.array(similarities)
        indexes = np.array(indexes)

        sorted_indexes = np.argsort(similarities)[::-1]
        return indexes[sorted_indexes[:n]], similarities[sorted_indexes[:n]].reshape(-1, 1)

    def get_similar_by_tfidf(self, text, n):
        idx, _dist = self.get_similar_indexes(text, n, self.get_tfidf_embeddings)
        return np.hstack((self.dataset.iloc[idx], _dist))

    def get_similar_by_boolean(self, text, n):
        idx, _dist = self.get_similar_indexes(text, n, self.get_boolean_embeddings)
        return np.hstack((self.dataset.iloc[idx], _dist))

    def get_similar_by_word_embedding(self, text, n):
        idx, _dist = self.get_similar_indexes(text, n, self.get_word_cidf_embeddings)
        return np.hstack((self.dataset.iloc[idx], _dist))

    def get_similar_by_sentence_embedding(self, text, n):
        idx, _dist = self.get_similar_indexes(text, n, self.get_transformer_embeddings)
        return np.hstack((self.dataset.iloc[idx], _dist))


if __name__ == '__main__':

    df = pd.read_csv('../../resources/shahnameh-labeled.csv')
    model = Similarities(df)

    sample = 'خداوند نام و خداوند گنج - بدانکس که دل را به دانش بشست'

    print('sample: ', sample)

    print('-' * 100)
    for poem, _, dist in model.get_similar_by_tfidf(sample, 10):
        print("tfidf: {:50s} \t with similarity of {:.2f}".format(poem, dist))

    print('-' * 100)
    for poem, _, dist in model.get_similar_by_boolean(sample, 10):
        print("bools: {:50s} \t with similarity of {:.2f}".format(poem, dist))

    print('-' * 100)
    for poem, _, dist in model.get_similar_by_word_embedding(sample, 10):
        print("word: {:50s} \t with similarity of {:.2f}".format(poem, dist))

    print('-' * 100)
    for poem, _, dist in model.get_similar_by_sentence_embedding(sample, 10):
        print("sent: {:50s} \t with similarity of {:.2f}".format(poem, dist))
