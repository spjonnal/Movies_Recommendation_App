import requests, json,sys,os,time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/project/.cache/playwright"

def return_latest_information():
    with open("imdb_genres_page.txt") as url:
        imdb_url = url.read().strip()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        #page.set_viewport_size({"width": 1920, "height": 1080})
        
        page.goto(imdb_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(5000)

        html = page.content()
        browser.close()

    soup = bs(html, "lxml")

    movies = soup.select("li.ipc-metadata-list-summary-item")
    #print("movie information = ",movies)
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

    # --- Final JSON ---
    final_top_movies_json = {
        'movie_names': movie_headings,
        'images': images_sources,
        'release_time': release_year,
        'movie_length': runtime,
        'imdb_rating': movie_rating,
        'certificate': certificate
    }
    
    return final_top_movies_json
if __name__ == "__main__":
    
    
    top_suggested_movies = return_latest_information()
    sys.stdout.write(json.dumps(top_suggested_movies))
    sys.stdout.flush()
