import csv, collections, json, random
import tornado.ioloop
import tornado.web
from cuisine_recommend import CuisineRecommend
from fuzzywuzzy import fuzz

recipes = []
cr = CuisineRecommend()
search = []
ingredient_word = []

with open('cuisine_data.csv') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        name, recipe = row[2], row[-1][1:-1].split(", ")
        recipes.append((name, recipe))
        ingredient_word.extend(recipe)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok")

class IngredientHandler(tornado.web.RequestHandler):
    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        ingredient = []
        for p in param['data']:
            best_search = (0, "")
            for i in ingredient_word:
                score = fuzz.ratio(p, i)
                if score > best_search[0]:
                    best_search = (score, i)
            ingredient.append(best_search[1])
        result = []
        for id, recipe in enumerate(recipes):
            cnt = 0
            for i in param['data']:
                if i in recipe[1]:
                    cnt += 1
            if cnt == len(param['data']):
                result.append(id)
        result.sort(key=lambda id : len(recipes[id][1]))
        recipe = []
        for i in result[:3]:
            search.append(i)
            recipe.append(recipes[i])
            if len(search) > 10:
                search.pop(0)
        if len(recipe) > 0:
            res = json.dumps({'res': recipe})
        else:
            res = json.dumps({'error': 'not found'})
        self.write(res)

class CuisineHandler(tornado.web.RequestHandler):
    def get(self, id):
        id = int(id)
        res = json.dumps({'res': recipes[id]})
        self.write(res)

class RecommendHandler(tornado.web.RequestHandler):
    def get(self):
        recommend = cr.predict(search).tolist()
        recipe = []
        print(recommend)
        for i in recommend[1:4]:
            recipe.append(recipes[i])
        res = json.dumps({'res': recipe})
        self.write(res)

class SearchHandler(tornado.web.RequestHandler):
    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        best_search = (0, "")
        for idx, recipe in enumerate(recipes):
            score = fuzz.ratio(param['data'], recipe[0])
            if score > best_search[0]:
                best_search = (score, idx)
        
        print(best_search[0], recipes[best_search[1]])

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/ingredient", IngredientHandler),
        (r"/api/recommend", RecommendHandler),
        (r"/api/cuisine/([0-9]+)", CuisineHandler),
        (r"/api/search", SearchHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
