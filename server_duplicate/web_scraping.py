import json, sys, os, time
from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/opt/render/project/.cache/playwright"

def return_latest_information():
    with open("imdb_genres_page.txt") as f:
        imdb_url = f.read().strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-extensions'
            ]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        # PRODUCTION: Handle Render slowness + bot detection
        page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda route: route.abort())  # Block images/fonts
        page.route("**/ads*", lambda route: route.abort())  # Block ads/trackers
        
        try:
            page.goto(imdb_url, wait_until="domcontentloaded", timeout=20000)
            
            # CRITICAL: Wait for ACTUAL movie list (Render needs this)
            page.wait_for_selector("li[class*='ipc-metadata-list-summary-item'], li[data-testid='list-item'], .ipc-list li", timeout=20000)
            
            # Quick scroll for lazy content
            page.evaluate("window.scrollTo(0, 2500);")
            page.wait_for_timeout(3000)
            
            html = page.content()
        except Exception as e:
            html = page.content()  # Fallback: grab whatever loaded
    #        print(f"Wait timeout (normal on slow Render): {e}")
        finally:
            browser.close()
    
    soup = bs(html, "lxml")
    
    # ROBUST SELECTOR: Multiple fallbacks
    movies = (soup.select("li.ipc-metadata-list-summary-item") or
              soup.select("li[data-testid='list-item']") or
              soup.select("li[class*='ipc-list-item']") or
              soup.select("div[class*='ipc-metadata-list-summary-item']"))
    
    #print(f"Extracted {len(movies)} movies from {imdb_url}")
    
    if not movies:
        # Save for Render debug (logs)
        debug_info = {
            "error": "No movies found",
            "li_count": len(soup.find_all("li")),
            "h3_count": len(soup.find_all("h3")),
            "sample_title": soup.find("h3").text[:50] if soup.find("h3") else "None",
            "url": imdb_url
        }
        return debug_info
    
    # Your extraction (with fallbacks)
    images_sources, movie_headings, runtime, movie_rating, release_year, certificate = [], [], [], [], [], []
    
    for i in movies:
        # TITLE
        heading = i.find('h3') or i.find(class_=lambda x: x and 'ipc-title' in str(x))
        movie_headings.append(heading.text.strip()[:100] if heading else 'N/A')
        
        # IMAGE (try data-src too)
        img = i.find('img')
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
        images_sources.append(src if src else 'N/A')
        
        # METADATA
        meta_div = (i.find('div', class_=lambda x: x and 'cli-title-metadata' in str(x)) or
                   i.find(class_=lambda x: x and 'ipc-metadata-list-item' in str(x)))
        spans = meta_div.find_all('span') if meta_div else []
        
        release_year.append(spans[0].text.strip() if len(spans) > 0 else 'N/A')
        runtime.append(spans[1].text.strip() if len(spans) > 1 else 'N/A')
        certificate.append(spans[2].text.strip() if len(spans) > 2 else 'N/A')
        
        # RATING
        rating_container = i.find('div', class_=lambda x: x and 'cli-ratings-container' in str(x))
        if not rating_container:
            rating_container = i.find(class_=lambda x: x and 'rating' in str(x).lower())
        
        rating_span = (rating_container.find('span', class_=lambda x: x and 'ipc-rating-star--rating' in str(x)) if rating_container else None)
        movie_rating.append(rating_span.text.strip() if rating_span else 'N/A')
    
    return {
        'Movie Name': movie_headings,
        #'images': images_sources,
        'Release Date': release_year,
        'Runtime': runtime,
        'IMDB Rating': movie_rating,
        'Certificate': certificate,
        
    }

if __name__ == "__main__":
    result = return_latest_information()
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
