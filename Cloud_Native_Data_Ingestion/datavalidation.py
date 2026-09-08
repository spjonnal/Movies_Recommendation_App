from datetime import datetime

# Syntactic Validation - It is useful in stopping invalid or unsecure data to our db because we accept data only in specific format
def syntactic_validation(title,genres,overview,release_date,ratings,imdb_id,adult_rated,org_lang,yt_tr,length,cast):
    
    errors = []
    try:
        if not isinstance(title, str):
            errors.append(f"{title} is not a valid instance of string")
        if not isinstance(genres,list):
            errors.append(f"{genres} are not a valid instance of list")
        if not isinstance(overview, str):
            errors.append(f"overview of {title} is not a valid instance of string")
        if not isinstance(ratings, (int,float)):
            errors.append(f"{ratings} is not a valid instance of float")
        if not isinstance(imdb_id, str):
            errors.append(f"{imdb_id} is not a valid instance of string")
        if not isinstance(adult_rated, bool):
            errors.append(f"{adult_rated} is not a valid instance of boolean")
        if not isinstance(org_lang, str):
            errors.append(f"{org_lang} is not a valid instance of string")
        if not isinstance(yt_tr, str):
            errors.append(f"{yt_tr} is not a valid instance of string")
        if not isinstance(length, int):
            errors.append(f"{length} is not a valid instance of integer")
        if not isinstance(cast, list):
            errors.append(f"{cast} is not a valid instance of list")
        try:
            datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError:
            errors.append(f"{release_date} is not a valid date format")
        
        return errors
        
    except Exception as e:
        return f"Movie validation failed: {str(e)}"


#Semantic Validation - checking if the data makes sense. It make be syntactically correct but a movie runtime of 0 seconds does not makes sense.

def semantic_validation(title,genres,overview):
    errors = []
    if  title.strip() is None:
        errors.append(f"{title} is invalid")
    if not len(genres)> 0:
        errors.append(f"invalid genres information for {title}")
    if not len(overview) >0:
        errors.append(f"invalid overview information for {title}")
    return errors
def range_validation(title,release_date,ratings,length):
    errors=[]
    release_time = release_date.split('-')
    year = int(release_time[0])
    if year > (datetime.now().year + 10):
        errors.append(f"{title} release date is more than a decade. Ignore this if possible!")
    if ratings <=0 or ratings > 10:
        errors.append(f"better not include {title} due to improper ratings {ratings}")
    if length <= 10:
        errors.append(f"{title} runtime is quie low :{length}, making it suspicious")
    return errors
def required_fields_check(title,genres,runtime,imdb_id,release_date,ratings,yt_tr,adult_rated):
    errors = []
    if not title or title.strip() == "" or len(genres) == 0 or runtime == 0 or imdb_id is None or release_date is None or ratings is None or yt_tr is None or adult_rated is None:
        errors.append(f"Do not include {title or 'this'} movie as certain required fields are missing")
    return errors

def implement_data_validation(movie_info):
    consolidated_errors = []
    title = movie_info['title']
    genres = movie_info['genres']
    overview = movie_info['overview']
    release_date = movie_info['release_date']
    ratings = movie_info['ratings']
    imdb_id = movie_info['imdb_id']
    adult_rated = movie_info['adult_rated']
    org_lang = movie_info['original_language']
    yt_tr = movie_info['youtube_trailer']
    length = movie_info['runtime']
    cast = movie_info['cast']

    consolidated_errors.extend(syntactic_validation(title,genres,overview,release_date,ratings,imdb_id,adult_rated,org_lang,yt_tr,length,cast))
    consolidated_errors.extend(semantic_validation(title,genres,overview))
    consolidated_errors.extend(range_validation(title,release_date,ratings,length))
    consolidated_errors.extend(required_fields_check(title,genres,length,imdb_id,release_date,ratings,yt_tr,adult_rated))
    # Data Quality reporting
    return {
        'movie':title,
        'status': "success" if not consolidated_errors else "failed validation due to errors",
        'errors':consolidated_errors
    }

# if __name__ == "__main__":

#     implement_data_validation(movie_info)