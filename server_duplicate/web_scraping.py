import requests, json,sys
from bs4 import BeautifulSoup as bs

def return_latest_information():

    with open("imdb_genres_page.txt") as url:
        imdb_url = url.read().strip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }


    req = requests.get(imdb_url,headers=headers)
    parsed_content = bs(req.content,"html.parser")


    movies = parsed_content.find_all('li', class_=lambda x: x and 'ipc-metadata-list-summary-item' in x)

    images_sources = []
    movie_headings = []
    runtime = []
    movie_rating = []
    release_year = []
    certificate = []

    for i in movies:
        # --- Extract title ---
        heading = i.find('h3')
        movie_headings.append(heading.text.strip() if heading else 'N/A')

        # --- Extract poster image ---
        img = i.find('img')
        images_sources.append(img.get('src') if img else 'N/A')

        # --- Extract release year, duration, certificate ---
        meta_div = i.find('div', attrs={"class": lambda x: x and 'cli-title-metadata' in x})
        spans = meta_div.find_all('span') if meta_div else []

        release_year.append(spans[0].text.strip() if len(spans) >= 1 else 'N/A')
        runtime.append(spans[1].text.strip() if len(spans) >= 2 else 'N/A')
        certificate.append(spans[2].text.strip() if len(spans) >= 3 else 'N/A')

        # --- Extract IMDb rating ---
        rating_container = i.find('div', attrs={"class": lambda x: x and 'cli-ratings-container' in x})
        if rating_container:
            rating_span = rating_container.find('span', attrs={"class": lambda x: x and 'ipc-rating-star--rating' in x})
            movie_rating.append(rating_span.text.strip() if rating_span else 'N/A')
        else:
            movie_rating.append('N/A')

    

    final_top_movies = {
        'Movie Name': movie_headings,
        'Release Date': release_year,
        'Movie Length': runtime,
        'IMDB Rating': movie_rating,
        'Certificate': certificate
    }
    
    return final_top_movies
if __name__ == "__main__":
    top_suggested_movies = return_latest_information()
   
    sys.stdout.write(json.dumps(top_suggested_movies))
    sys.stdout.flush()

