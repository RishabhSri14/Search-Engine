import pandas as pd
import numpy as np

# movie = pd.read_csv('./archive/movie.csv')
# rating = pd.read_csv('./archive/rating.csv')
data  = pd.read_csv('./processed_data.csv')
print(data.shape,data['movieId'].nunique(),data['userId'].nunique())
USER_ID = 7
user_df = data[data['userId']==USER_ID]
print(user_df.shape,user_df['movieId'].nunique())
