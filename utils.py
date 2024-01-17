import pandas as pd
import numpy as np

# Hybrid Recommender
def get_recos(user_id):
    user_id = int(user_id)
    #getting dataset
    movie = pd.read_csv('./static/dataset/movie.csv')
    rating = pd.read_csv('./static/dataset/rating.csv')
    data  = pd.read_csv('./static/dataset/processed_data.csv')
    print(rating.keys())
    movies_avg_rating = data.groupby('movieId').agg('mean')
    user_df = data[data['userId']==user_id]
    movies_watched = user_df['movieId'].unique()
    
    # getting users who have watched 60% of movies watched by user 1
    similar_users = data[data['movieId'].isin(user_df['movieId'])].groupby(['userId'])['movieId'].count().reset_index().sort_values(by='movieId',ascending=False)
    similar_users=similar_users[similar_users['movieId']>=0.6*user_df['movieId'].nunique()]
    similar_users = similar_users['userId'].tolist()    
    
    #getting 2-D matrix of rating values for movies watched by similar users
    corr = data[data['userId'].isin(similar_users)]
    mat =corr.pivot_table(index='userId',columns='movieId',values='rating')
    
    # Collaborative filtering
    
    #Getting correlation matrix between users
    corr_df = pd.DataFrame(mat.T.corr().unstack().sort_values(), columns=['corr'])
    corr_df.index.names = ['user_id_1', 'user_id_2']
    corr_df.reset_index(inplace=True)
    
    # getting pearson correlation between given user and other users
    top_users = corr_df[(corr_df["user_id_1"] == user_id) & (corr_df["corr"] >= corr_df['corr'].mean())][["user_id_2", "corr"]].reset_index(drop=True).sort_values(by="corr", ascending=False)
    top_users.rename(columns={"user_id_2": "userId"}, inplace=True)
    top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')
    top_users_ratings = top_users_ratings[top_users_ratings["userId"] != user_id]
    
    # getting weighted rating for each movie
    top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']
    recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
    recommendation_df = recommendation_df.reset_index()
    movies_to_recommend_collaborative = recommendation_df.sort_values(by='weighted_rating', ascending=False)
    
    # Content based filtering
    
    #getting movie id of most recent movie liked by user
    best_rating = rating[(rating["userId"] == user_id)].sort_values(by='rating', ascending=False)['rating'][0:1].values[0] 
    movie_id = rating[(rating["userId"] == user_id) & (rating["rating"] == best_rating)].sort_values(by="timestamp", ascending=False)["movieId"][0:1].values[0]
    recent_liked_movie = movie[movie["movieId"] == movie_id]["movieId"].values[0]
    movie_df = data[data["movieId"] == movie_id].sort_values(by='userId')
    temp = mat[recent_liked_movie]
    #getting correlation between most recent movie liked by user and other movies
    res = pd.DataFrame(mat.corrwith(temp).sort_values(ascending=False), columns=["corr"])
    movies_to_recommend_content = res.merge(movies_avg_rating, on='movieId').drop(['userId'],axis=1)
    movies_to_recommend_content['score']= movies_to_recommend_content['corr']*movies_to_recommend_content['rating']
    
    # Hybrid filtering
    
    recommedations = movies_to_recommend_collaborative.merge(movies_to_recommend_content,on='movieId').dropna()
    recommedations['final_score'] = (recommedations['score']+recommedations['weighted_rating'])/2
    recommedations = recommedations.merge(movie,on='movieId').sort_values(by='final_score',ascending=False)
    recommedations.drop(['corr','rating'],axis=1,inplace=True)
    return recommedations[['title','genres']].head(20)


def get_previous_movies(user_id):
    movie = pd.read_csv('./static/dataset/movie.csv')
    data  = pd.read_csv('./static/dataset/processed_data.csv')
    movies = data[data['userId']==int(user_id)].sort_values(by='rating',ascending=False)['movieId'].head(5)
    return (movie[movie['movieId'].isin(movies)].drop('movieId',axis=1)).reset_index().values.tolist()
    