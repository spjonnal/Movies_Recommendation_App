from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sdk.task import dag, task

from datetime import datetime, timedelta
from web_scrape import scrape_web_information, insert_movie_information
from datavalidation import implement_data_validation


default_args={
    'owner':'movie-data-pipeline',
    'retries':3,
    'retry_delay':timedelta(minutes=10)
}

@dag(
    dag_id = "data_ingestion_pipeline",
    default_args=default_args,
    description="Automation pipeline to extract, validate, transform and load data to database",
    schedule="0 0 * * *", # minute, hour, date, month, year this means every midnight, invoke this DAG
    catchup = False, # to not trigger this function for the dates before today.
    tags = ["ETL","movies","TMDB"],
)

def movie_data_ingestion_pipeline():
    @task
    def data_extraction():
        return scrape_web_information("https://api.themoviedb.org/3/discover/movie")
        
    @task
    def data_validation(data_to_insert):
        failed_movies = []
        validation_passed_movies = []
        for movie in data_to_insert:
                movie_status = implement_data_validation(movie)
                if movie_status and movie_status["status"] != "success":
                    failed_movies.append(movie['title'])
                else:
                    validation_passed_movies.append(movie)
        return validation_passed_movies
    @task
    def data_load(data_to_insert):
        c = 0
        for movie in data_to_insert:
            runtime = movie['runtime']
            hours = runtime//60
            minutes = runtime % 60
            movie['runtime'] = f"{hours}h:{minutes}m"
            insert_movie_information(movie)
            c += 1
        return f"Successfully inserted {c} movie(s)"
        
    entire_movies = data_extraction()
    validation_success_movies = data_validation(entire_movies)
    data_load(validation_success_movies)
    

    

movie_data_ingestion_pipeline()
    
        
if __name__ == "__main__":
     dag.test()