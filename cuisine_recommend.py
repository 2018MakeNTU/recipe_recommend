import csv
import numpy as np
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors

class CuisineRecommend:
    def __init__(self):
        self.recipes = []
        with open('cuisine_data.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                name, cuisine, ingredients = row[2], row[6][1:-1].split(", "), row[-1][1:-1].split(", ")
                self.recipes.append((name, cuisine, ingredients))

        cnt = Counter()
        for recipe in self.recipes:
            for ingredient in recipe[-1]:
                cnt[ingredient] += 1
        most_common = cnt.most_common(10)
        self.exclude = [i[0] for i in most_common]

        self.features = []
        for recipe in self.recipes:
            self.features.append(recipe[2].copy())

        for f in self.features:
            self.remove(f)

        self.le = DictVectorizer()
        features_preprocess = self.le.fit_transform([{i: 1 for i in f} for f in self.features])

        self.tsvd = TruncatedSVD(n_components=100)
        X = self.tsvd.fit_transform(features_preprocess)

        self.nbrs = NearestNeighbors(n_neighbors=10, algorithm='kd_tree').fit(X)

    def remove(self, feature):
        for e in self.exclude:
            if e in feature:
                feature.remove(e)

    def predict(self, ids):
        X = np.zeros((1, self.tsvd.n_components))
        for id in ids:
            f = self.features[id]
            f_pp = self.le.transform({i: 1 for i in f})
            X += self.tsvd.transform(f_pp)
        if len(ids) > 0:
            X /= len(ids)
        _, res = self.nbrs.kneighbors(X)
        return res[0]

if __name__ == '__main__':
    cr = CuisineRecommend()
    print(cr.predict([600]))
