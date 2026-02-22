import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import process

# Load data
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Extract year
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)

# Average ratings
avg_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
avg_ratings.columns = ['movieId', 'avg_rating']
movies = movies.merge(avg_ratings, on='movieId', how='left')

# Clean genres
movies['genres'] = movies['genres'].str.replace('|', ' ', regex=False)

# TF-IDF matrix — store this but don't compute full similarity matrix
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

def recommend(title, genre=None, min_rating=0, year_min=None, year_max=None, n=10):
    matched_title, score = process.extractOne(title, indices.index.tolist())
    if score < 60:
        return []

    idx = indices[matched_title]

    # Compute similarity only for this one movie instead of all movies
    movie_vector = tfidf_matrix[idx]
    sim_scores = cosine_similarity(movie_vector, tfidf_matrix).flatten()
    sim_scores[idx] = 0  # exclude the movie itself

    top_indices = sim_scores.argsort()[::-1]
    results = movies.iloc[top_indices].copy()

    if genre:
        results = results[results['genres'].str.contains(genre, case=False)]
    if min_rating:
        results = results[results['avg_rating'] >= float(min_rating)]
    if year_min:
        results = results[results['year'] >= float(year_min)]
    if year_max:
        results = results[results['year'] <= float(year_max)]

    return results['title'].head(n).tolist()