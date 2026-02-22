import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import process

# Load data
movies = pd.read_csv('ml-latest-small/movies.csv')
ratings = pd.read_csv('ml-latest-small/ratings.csv')

# Extract year from title
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)

# Compute average rating per movie
avg_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
avg_ratings.columns = ['movieId', 'avg_rating']
movies = movies.merge(avg_ratings, on='movieId', how='left')

# Clean genres
movies['genres'] = movies['genres'].str.replace('|', ' ', regex=False)

# ---- GENRE BASED SIMILARITY ----
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])
genre_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# ---- COLLABORATIVE FILTERING (SVD from scratch) ----
# Build user-movie ratings matrix
# Limit to most active users and most rated movies for performance
top_movies = ratings['movieId'].value_counts().head(500).index
top_users = ratings['userId'].value_counts().head(200).index

filtered = ratings[
    ratings['movieId'].isin(top_movies) &
    ratings['userId'].isin(top_users)
]

ratings_matrix = filtered.pivot_table(
    index='userId', columns='movieId', values='rating'
).fillna(0)

# Normalize by subtracting mean rating per user
ratings_norm = ratings_matrix.sub(ratings_matrix.mean(axis=1), axis=0)

# SVD decomposition
U, sigma, Vt = np.linalg.svd(ratings_norm.values, full_matrices=False)

# Keep top 50 latent factors
k = 20
U_k = U[:, :k]
sigma_k = np.diag(sigma[:k])
Vt_k = Vt[:k, :]

# Reconstruct movie similarity from latent factors
movie_factors = Vt_k.T  # shape: (movies, k)
collab_sim_matrix = cosine_similarity(movie_factors)

# Map movieId to index in ratings matrix
collab_movie_ids = ratings_matrix.columns.tolist()
collab_id_to_idx = {mid: i for i, mid in enumerate(collab_movie_ids)}

# ---- HYBRID RECOMMEND FUNCTION ----
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

def recommend(title, genre=None, min_rating=0, year_min=None, year_max=None, n=10):
    # Fuzzy match the title
    matched_title, score = process.extractOne(title, indices.index.tolist())
    if score < 60:  # if confidence is too low, return nothing
        return []

    idx = indices[matched_title]
    movie_id = movies.iloc[idx]['movieId']

    # Genre similarity scores
    genre_scores = list(enumerate(genre_sim[idx]))

    # Collaborative similarity scores
    if movie_id in collab_id_to_idx:
        collab_idx = collab_id_to_idx[movie_id]
        collab_scores = collab_sim_matrix[collab_idx]
    else:
        collab_scores = None

    # Blend scores
    blended = []
    for i, g_score in genre_scores:
        mid = movies.iloc[i]['movieId']
        if collab_scores is not None and mid in collab_id_to_idx:
            c_score = collab_scores[collab_id_to_idx[mid]]
            final_score = 0.4 * g_score + 0.6 * c_score  # weight collab more
        else:
            final_score = g_score
        blended.append((i, final_score))

    blended = sorted(blended, key=lambda x: x[1], reverse=True)
    blended = [b for b in blended if b[0] != idx]  # remove the input movie

    movie_indices = [b[0] for b in blended]
    results = movies.iloc[movie_indices].copy()

    # Apply filters
    if genre:
        results = results[results['genres'].str.contains(genre, case=False)]
    if min_rating:
        results = results[results['avg_rating'] >= float(min_rating)]
    if year_min:
        results = results[results['year'] >= float(year_min)]
    if year_max:
        results = results[results['year'] <= float(year_max)]

    return results['title'].head(n).tolist()