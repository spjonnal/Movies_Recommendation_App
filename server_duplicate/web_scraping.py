import requests, json,sys,os,time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from playwright.sync_api import sync_playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/project/.cache/playwright"

def return_latest_information():
    start_time = time.time()
    
    with open("imdb_genres_page.txt") as f:
        imdb_url = f.read().strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        page.goto(imdb_url, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(5000)

        html = page.content()
        browser.close()
    
    soup = bs(html, "lxml")
    
    # Updated selectors for moviemeter/chart pages
    movies = soup.find_all('li', {'data-testid': 'list-item'}) or \
             soup.find_all('li', class_=lambda x: x and any(cls in str(x) for cls in ['ipc-list', 'metadata-list']))[:20]
    
    
    
    if not movies:
        return json.dumps({"error": "Selector mismatch - page loaded but no movies"}, indent=4)
    
    # Your extraction code (may need minor selector tweaks)...
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
    final_top_movies_json = json.dumps({
        'movie_names': movie_headings,
        'images': images_sources,
        'release_time': release_year,
        'movie_length': runtime,
        'imdb_rating': movie_rating,
        'certificate': certificate
    }, indent=4)
    
    return final_top_movies_json

if __name__ == "__main__":
    
    
    top_suggested_movies = return_latest_information()
    print(json.dumps(top_suggested_movies))
    sys.stdout.flush()
