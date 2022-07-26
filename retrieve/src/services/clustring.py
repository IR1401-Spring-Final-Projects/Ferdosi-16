import hazm
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import logging
import pickle
import tqdm
import os
from sklearn.decomposition import PCA

from sklearn.cluster import KMeans
from transformers import AutoTokenizer, AutoModel, AutoConfig

sns.set()
logger = logging.getLogger(__name__)
normalizer = hazm.Normalizer(token_based=True)


class Clustering:

    def __init__(self, dataset, k, pca_dim=8, max_iter=2_000, _checkpoint=None):

        model_name = 'HooshvareLab/bert-base-parsbert-uncased'
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, local_files_only=True)
        self.embedder = AutoModel.from_pretrained(
            model_name, local_files_only=True, config=AutoConfig.from_pretrained(model_name))

        self.directory = _checkpoint
        self.dataset = dataset.sort_values('text')
        self.dataset['text'] = self.dataset['text'].apply(normalizer.normalize)

        try:

            self.load_pca()
            self.load_kmeans()
            self.dataset['cluster_id'] = self.labels
            self.cluster_labels = self.generate_cluster_labels()
            return

        except:
            logger.warning('It is not possible to load models. Again the models are trained.')

        texts = self.dataset['text'].tolist()
        self.embeddings = self.get_transformer_embeddings(texts)

        self.pca = PCA(n_components=pca_dim)
        self.embeddings = self.pca.fit_transform(self.embeddings)

        self.kmeans = KMeans(n_clusters=k, max_iter=max_iter)
        self.labels = self.kmeans.fit_predict(self.embeddings)

        self.directory = '../../resources/clustering/'
        if not os.path.exists(self.directory): os.mkdir(self.directory)

        self.save_pca()
        self.save_kmeans()
        self.dataset['cluster_id'] = self.labels
        self.cluster_labels = self.generate_cluster_labels()

    def generate_cluster_labels(self):
        return self.dataset.groupby(['cluster_id', 'labels'])['text'] \
            .agg(['count']).sort_values('count', ascending=False).reset_index() \
            .groupby('cluster_id')['labels'].apply(lambda x: list(x)[:3])

    @staticmethod
    def _batch_series(iterable, n=2_000):
        for ndx in range(0, len(iterable), n): yield iterable[ndx:min(ndx + n, len(iterable))]

    def get_transformer_embeddings(self, documents):
        result = None
        for batch in tqdm.tqdm(self._batch_series(documents, 1_000)):
            output = self.embedder(**self.tokenizer(batch, return_tensors='pt', padding=True))
            output = np.mean(output.last_hidden_state.detach().numpy(), axis=1)
            result = np.concatenate((result, output)) if result is not None else output

        return result

    def load_pca(self):
        self.pca = pickle.load(
            open(os.path.join(self.directory, 'pca_model.dump'), 'rb'))
        self.embeddings = pickle.load(
            open(os.path.join(self.directory, 'pca_embeddings.dump'), 'rb'))

    def save_pca(self):
        pickle.dump(
            self.pca, open(os.path.join(self.directory, 'pca_model.dump'), 'wb'))
        pickle.dump(
            self.embeddings, open(os.path.join(self.directory, 'pca_embeddings.dump'), 'wb'))

    def load_kmeans(self):
        self.kmeans = pickle.load(
            open(os.path.join(self.directory, 'kmeans_model.dump'), 'rb'))
        self.labels = pickle.load(
            open(os.path.join(self.directory, 'kmeans_labels.dump'), 'rb'))

    def save_kmeans(self):
        pickle.dump(
            self.kmeans, open(os.path.join(self.directory, 'kmeans_model.dump'), 'wb'))
        pickle.dump(
            self.labels, open(os.path.join(self.directory, 'kmeans_labels.dump'), 'wb'))

    def predict_cluster(self, element):
        embedding = self.get_transformer_embeddings([element])
        embedding = self.pca.transform(embedding)
        cluster_id = self.kmeans.predict(embedding)[0]
        return cluster_id, self.cluster_labels[cluster_id]

    def plot_clusters(self, n=1_000):
        pca = PCA(n_components=2)
        sample = np.random.randint(0, self.embeddings.shape[0], n)
        mini_embeddings = pca.fit_transform(self.embeddings[sample])

        sns.scatterplot(
            x=mini_embeddings[:, 0],
            y=mini_embeddings[:, 1], c=self.labels[sample], cmap='cool')

        sns.scatterplot(
            x=self.kmeans.cluster_centers_[:, 0],
            y=self.kmeans.cluster_centers_[:, 1], c=['black'])

        plt.show()


if __name__ == '__main__':
    df = pd.read_csv('../../resources/shahnameh-labeled.csv')

    checkpoint = '../../resources/clustering'
    model = Clustering(df, 9, _checkpoint=None)
    model.plot_clusters()

    cid, labels = model.predict_cluster('رستم رفت جنگ و سهراب سوییچ رخش را برداشت رفت توران')
    print('labels: ', labels)
