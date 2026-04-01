import pandas as pd

movie_data = pd.read_csv('final_movie_data.csv')
movie_data['Youtube Trailer Links'] = ''

for i in range(movie_data.shape[0]):
    movie_name = movie_data['Title'].iloc[i]
    if(not isinstance(movie_name, float)):
        
        splitted_movie_name = movie_name.split(' ')        
        movie_to_attach = ' '
        for j in splitted_movie_name:
            movie_to_attach += j+'+'
        youtube_link = f"https://www.youtube.com/results?search_query={movie_to_attach}official+trailer"
        movie_data.loc[i,'Youtube Trailer Links'] = youtube_link
        
print("final movie = ",movie_data)
movie_data.to_csv('Movie data with trailer links.csv',index = None)