# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# Создание моделей Schema
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Movie created", 201


# ----------MovieViews--------------
@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "Movie not found", 404
        return movie_schema.dump(movie), 200

    def put(self, mid):
        updated_rows = db.session.query(Movie).filter(Movie.id == mid).update(request.json)
        if updated_rows != 1:
            return "Not updated", 400
        db.session.commit()
        return "", 204
        # movie = Movie.query.get(mid)
        # req_json = request.json
        # movie.title = req_json.get("title")
        # movie.description = req_json.get("descriptionl")
        # movie.trailer = req_json.get("trailer")
        # movie.year = req_json.get("year")
        # movie.rating = req_json.get("rating")
        # movie.genre_id = req_json.get("genre_i")
        # movie.director_id = req_json.get("director_id")
        # db.session.add(movie)
        # db.session.commit()
        return "", 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "Movie not found", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


# ----------GenreViews-----------------
@genre_ns.route('/')
class GenreViews(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Genre created", 201


@genre_ns.route('/<gid>')
class GenreView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        return genre_schema.dump(genre), 200

    def put(self, gid):
        updated_rows = db.session.query(Genre).filter(Genre.id == gid).update(request.json)
        if updated_rows != 1:
            return "Not updated", 400
        db.session.commit()
        return "", 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        if genre is None:
            return "Genre not found", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


# ----------DirectorViews--------------
@director_ns.route('/')
class DirectorViews(Resource):
    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Director created", 201


@director_ns.route('/<did>')
class DirectorView(Resource):
    def get(self, did):
        try:
            director = Director.query.get(did)
            return director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404

    def put(self, did):
        updated_rows = db.session.query(Director).filter(Director.id == did).update(request.json)
        if updated_rows != 1:
            return "Not updated", 400
        db.session.commit()
        return "", 204

    def delete(self, did):
        director = Director.query.get(did)
        if not director:
            return "Movie not found", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
