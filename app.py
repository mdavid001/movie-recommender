from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300"

def get_poster(title):
    try:
        # Strip year from title e.g "Toy Story (1995)" → "Toy Story"
        clean_title = title.split(" (")[0]
        res = requests.get(TMDB_SEARCH_URL, params={
            "api_key": TMDB_API_KEY,
            "query": clean_title
        })
        data = res.json()
        if data['results'] and data['results'][0]['poster_path']:
            return TMDB_IMAGE_BASE + data['results'][0]['poster_path']
    except:
        pass
    return None

@app.route('/recommend', methods=['GET'])
def get_recommendations():
    title = request.args.get('title')
    genre = request.args.get('genre', None)
    min_rating = float(request.args.get('min_rating', 0))
    year_min = request.args.get('year_min', None)
    year_max = request.args.get('year_max', None)

    if year_min:
        year_min = float(year_min)
    if year_max:
        year_max = float(year_max)

    if not title:
        return jsonify({'error': 'Please provide a movie title'}), 400

    results = recommend(title, genre=genre, min_rating=min_rating, year_min=year_min, year_max=year_max)

    if not results:
        return jsonify({'error': 'Movie not found or no results match filters'}), 404

    # Fetch posters for each result
    movies_with_posters = []
    for movie in results:
        movies_with_posters.append({
            "title": movie,
            "poster": get_poster(movie)
        })

    return jsonify({'movie': title, 'recommendations': movies_with_posters})

@app.route('/random', methods=['GET'])
def random_movie():
    import pandas as pd
    movies = pd.read_csv('ml-latest-small/movies.csv')
    movie = movies.sample(1).iloc[0]
    return jsonify({'title': movie['title']})

if __name__ == '__main__':
    app.run(debug=True)