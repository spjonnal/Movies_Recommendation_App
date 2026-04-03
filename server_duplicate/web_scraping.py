# import json, sys, os, time
# from bs4 import BeautifulSoup as bs
# from playwright.sync_api import sync_playwright

# #os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/project/.cache/playwright"

# def return_latest_information():
#     with open("imdb_genres_page.txt") as f:
#         imdb_url = f.read().strip()
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=True,
#             args=[
#                 '--no-sandbox',
#                 '--disable-setuid-sandbox',
#                 '--disable-dev-shm-usage',
#                 '--disable-gpu',
#                 '--no-first-run',
#                 '--no-zygote',
#                 '--single-process',
#                 '--disable-extensions'
#             ]
#         )
#         page = browser.new_page(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
#             viewport={"width": 1920, "height": 1080}
#         )
#         # PRODUCTION: Handle Render slowness + bot detection
#         page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())  # Block images/fonts
#         page.route("**/ads*", lambda route: route.abort())  # Block ads/trackers
#         html = ""
#         try:
#             page.goto(imdb_url, wait_until="domcontentloaded", timeout=50000)
#             print("Page loaded, title:", page.title())
#             # CRITICAL: Wait for ACTUAL movie list (Render needs this)
#             #page.wait_for_selector("li[class*='ipc-metadata-list-summary-item'], li[data-testid='list-item'], .ipc-list li", timeout=20000)
#             page.wait_for_selector("body",timeout = 500000)
#             # Quick scroll for lazy content
#             page.evaluate("window.scrollTo(0, 2500);")
#             page.wait_for_timeout(10000)
            
#             html = page.content()
#             print("html = ",html)
#         except Exception as e:
            
#             print(f"Wait timeout (normal on slow Render): {e}")
#         finally:
#             browser.close()
    
#     soup = bs(html, "lxml")
    
#     # ROBUST SELECTOR: Multiple fallbacks
#     movies = (soup.select("li.ipc-metadata-list-summary-item") or
#               soup.select("li[data-testid='list-item']") or
#               soup.select("li[class*='ipc-list-item']") or
#               soup.select("div[class*='ipc-metadata-list-summary-item']"))
    
#     #print(f"Extracted {len(movies)} movies from {imdb_url}")
    
#     if not movies:
#         # Save for Render debug (logs)
#         debug_info = {
#             "error": "No movies found",
#             "li_count": len(soup.find_all("li")),
#             "h3_count": len(soup.find_all("h3")),
#             "sample_title": soup.find("h3").text[:50] if soup.find("h3") else "None",
#             "url": imdb_url
#         }
#         return debug_info
    
#     # Your extraction (with fallbacks)
#     images_sources, movie_headings, runtime, movie_rating, release_year, certificate = [], [], [], [], [], []
    
#     for i in movies:
#         # TITLE
#         heading = i.find('h3') or i.find(class_=lambda x: x and 'ipc-title' in str(x))
#         movie_headings.append(heading.text.strip()[:100] if heading else 'N/A')
        
#         # IMAGE (try data-src too)
#         img = i.find('img')
#         src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
#         images_sources.append(src if src else 'N/A')
        
#         # METADATA
#         meta_div = (i.find('div', class_=lambda x: x and 'cli-title-metadata' in str(x)) or
#                    i.find(class_=lambda x: x and 'ipc-metadata-list-item' in str(x)))
#         spans = meta_div.find_all('span') if meta_div else []
        
#         release_year.append(spans[0].text.strip() if len(spans) > 0 else 'N/A')
#         runtime.append(spans[1].text.strip() if len(spans) > 1 else 'N/A')
#         certificate.append(spans[2].text.strip() if len(spans) > 2 else 'N/A')
        
#         # RATING
#         rating_container = i.find('div', class_=lambda x: x and 'cli-ratings-container' in str(x))
#         if not rating_container:
#             rating_container = i.find(class_=lambda x: x and 'rating' in str(x).lower())
        
#         rating_span = (rating_container.find('span', class_=lambda x: x and 'ipc-rating-star--rating' in str(x)) if rating_container else None)
#         movie_rating.append(rating_span.text.strip() if rating_span else 'N/A')
    
#     return {
#         'Movie Name': movie_headings,
#         #'images': images_sources,
#         'Release Date': release_year,
#         'Runtime': runtime,
#         'IMDB Rating': movie_rating,
#         'Certificate': certificate,
        
#     }

# if __name__ == "__main__":
#     result = return_latest_information()
#     print(result)
#     # sys.stdout.write(json.dumps(result))
#     # sys.stdout.flush()


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import psycopg2
from dotenv import load_dotenv
import json, sys,os


#load_dotenv("pg_admin4_connect_for_py.env")

pg_host = os.getenv("DB_HOST")
pg_db_name = os.getenv("DB_NAME")
pg_user = os.getenv("DB_USER") 
pg_port = os.getenv("DB_PORT")
pg_password = os.getenv("DB_PASSWORD")

db_connection = psycopg2.connect(
    host=pg_host,
    database = pg_db_name,
    user=pg_user,
    port = pg_port,
    password = pg_password
)

cursor = db_connection.cursor()


with open("imdb_genres_page.txt") as i:
    imdb_url = i.read().strip()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # IMPORTANT
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    page.goto(imdb_url, wait_until="domcontentloaded", timeout=50000)
    page.wait_for_timeout(5000)
    
    try:
        
        script_tag = page.query_selector_all(
            'script[type="application/ld+json"]'
        )
        
        cursor.execute(f"select movie_name from trending_movies")
        existing_titles = cursor.fetchall()
        existing_titles = [title[0] for title in existing_titles]
        print("esisting data = ",existing_titles)
        for script in script_tag:

            script_content = script.text_content()
            
            data = json.loads(script_content)
            

            for movie_info in data.get("itemListElement", []):
                item = movie_info.get("item", {})
                if not isinstance(item, dict):
                    continue  # skip if something weird is there

                movie_data = {
                    "title": item.get("name", "N/A"),
                    "overview": item.get("description", "N/A"),
                    "rating": item.get("aggregateRating", {}).get("ratingValue", "N/A"),
                    "rating_count": item.get("aggregateRating", {}).get("ratingCount", "N/A"),
                    "genre": item.get("genre", "N/A"),
                    "duration": item.get("duration", "N/A")[2:],
                    "image": item.get("image", "N/A"),
                    "url": item.get("url", "N/A"),
                    "certificate": item.get("contentRating", "N/A"),
                }
                if movie_data['title'] not in existing_titles:
                    print("came to enter movie name = ",type(movie_data['certificate']),type(movie_data['rating']))
                    cursor.execute(
                        """
                        INSERT INTO trending_movies (runtime, imdb_ratings,certificate,overview,imdb_url_page,
                        genre,image_url,movie_name)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            movie_data['duration'],str(movie_data['rating']),movie_data['certificate'],movie_data['overview'],
                            movie_data['url'],movie_data['genre'],movie_data['image'],movie_data['title']
                        )
                    )  
                    cursor.execute(
                        """commit;"""
                    )  
                else:
                    print(f"movie name {movie_data['title']} already exists in DB")    
    except Exception as e:
        print(f"Error fetching page content: {e}")
        sys.exit(1)
    finally:
        browser.close()
