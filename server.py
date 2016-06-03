# -*- coding: utf-8 -*-

from flask import Flask

from recommendation import recommend

app = Flask(__name__)


@app.route("/<user_id>")
def recommend_movie_to_user(user_id):
    rec_movies = recommend(user_id)
    response = ''
    for movie in rec_movies:
        response += 'recommend: %s' % movie[0].encode('utf-8')
        response += '<br />'
        response += 'reason: %s' % ' '.join([m.encode('utf-8') for m in movie[1]['reason']])
        response += '<br /><br />'
    return response


@app.route("/")
def index():
    return "Welcome kira's movie recommendation system!"


if __name__ == "__main__":
    app.run(debug=True)