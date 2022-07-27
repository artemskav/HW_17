from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

import models
from models import *
from schems import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies_query = db.session.query(models.Movie)
        args_query = request.args
        director_id = args_query.get('director_id')
        genre_id = args_query.get('genre_id')
        if director_id is not None:
            movies_query = db.session.query(models.Movie).filter(models.Movie.director_id == director_id)
        if genre_id is not None:
            movies_query = db.session.query(models.Movie).filter(models.Movie.genre_id == genre_id)
        movies = movies_query.all()
        return movies_schema.dump(movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Add - Ok", 201


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        try:
            movie = Movie.query.get(uid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "", 404

    def put(self, uid):
        movie = db.session.query(models.Movie).filter(models.Movie.id == uid).first()
        if not movie:
            return "", 404
        movie_update = request.json
        movie.title = movie_update.get('title')
        movie.description = movie_update.get('description')
        movie.trailer = movie_update.get('trailer')
        movie.year = movie_update.get('year')
        movie.rating = movie_update.get('rating')
        db.session.add(movie)
        db.session.commit()
        return "обновлено", 204

    def delete(self, uid):
        movie = db.session.query(models.Movie).filter(models.Movie.id == uid).first()
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        db.session.close()
        return "delete - Ok", 204

@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        director = Director.query.all()
        return directors_schema.dump(director), 200

@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        try:
            director = Director.query.get(uid)
            return director_schema.dump(director), 200
        except Exception as e:
            return "", 404


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = Genre.query.all()
        return genres_schema.dump(genres), 200

@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):
        try:
            genre = Genre.query.get(uid)
            return genre_schema.dump(genre), 200
        except Exception as e:
            return "", 404

if __name__ == '__main__':
    app.run(debug=True)
