const sqdb = require("sqlite3").verbose()
const fs = require("fs")
const csv_parse = require("csv-parser")
const { resolve } = require("path")
const { rejects } = require("assert")
const {Client, Pool} = require("pg")
function db_connection(){
    const db = new sqdb.Database("sqdb.db",sqdb.OPEN_READWRITE,(err)=>{
        if(err){
            console.error(err.message)
        }
        
    })
    return db
}

const pg_pool = new Pool({
    host : process.env.DB_HOST,
    database:process.env.DB_NAME,
    user:process.env.DB_USER,
    password:process.env.DB_PASSWORD,
    port:5432,
    ssl: {
    rejectUnauthorized: false, // REQUIRED for Render
  },
});

function movie_recom_table_create(db){
    console.log("came to create a table",db)

        {
            db.run(`CREATE TABLE IF NOT EXISTS movie_information(
                "Adult Rated" BOOLEAN,
                "IMDB ID" NUMBER,
                Overview TEXT,
                "Release Date" DATE,
                Runtime Varchar (10),
                Title TEXT,
                Ratings FLOAT,
                Genres TEXT,
                "Available Languages" TEXT,
                "Cast and Crew" TEXT)`,(err)=>{
                if(err){
                    console.error("error thrown in movie data info table creation ->",err.message);
                }
                else{
                    console.log("Table movie_information created successfully");
                    
                }
            });
        }
    // });
    
}

function dropTable() {
    db = db_connection();
    db.run(`DROP TABLE IF EXISTS movie_information`, (err) => {
        if (err) {
            console.error('Error dropping table:', err.message);
        } else {
            console.log('Table dropped successfully.');
       
        }
    });
}
function getCount() {
    return new Promise((resolve, reject) => {
        const db = db_connection();
        db.get(`SELECT COUNT(*) as count FROM movie_information`, (err, row) => {
            if (err) {
                console.error("Unable to fetch the data", err.message);
                reject(err);
            } else {
                const count = row ? row.count : 0;
                console.log("the total rows in the dataset = ", count);
                resolve(count);
            }
        });
    });
}

async function InsertIntoDB(db) {
    return new Promise((resolve, reject) => {

            const data_result = [];
            fs.createReadStream('./final_movie_data.csv')
                .pipe(csv_parse({}))
                .on('data', (data) => data_result.push(data))
                .on('end', () => {
                    if (data_result.length === 0) return resolve();

                    let completed = 0;

                    data_result.forEach((row) => {
                        db.run(
                            `INSERT INTO movie_information (
                                "Adult Rated" ,"IMDB ID", Overview, "Release Date", Runtime, Title ,
                                Ratings, Genres, "Available Languages" , "Cast and Crew" 
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                            [
                                row["Adult Rated"] === 1, row["IMDB ID"], row['Overview'],
                                row["Release Date"], row['Runtime'],
                                row['Title'], row['Ratings'],
                                row['Genre'], row["Available Languages"],row["Cast and Crew"]
                            ],
                            (err) => {
                                if (err) console.error("Insert error:", err.message);

                                completed++;
                                if (completed === data_result.length) {
                                    console.log("All rows inserted successfully");
                                    resolve();
                                }
                            }
                        );
                    });
                })
                .on('error', (err) => reject(err));
        });
    // });
}



function dataCheck(){
    db = db_connection();
    db.get("SELECT COUNT(*) AS count from movie_information",(err,row)=>{
        if(err){
            console.error("Some error. Mode details ->",err.message);
        }
        if(row.count <1){
            console.log("No data exists. Inserting data",row.count);
            InsertIntoDB();
        }
        else{
            console.log("Data Already Exists in the table");
        }

    });
} 
function tableCheck(){
    db.run("SELECT name FROM sqlite_master WHERE type = 'table' and name = 'movie_information'",(err)=>{
        if(err){
            console.error("SOme error more information ->",err.message);
        }
        else{
            console.log("Table exisits");
        }
    })
}
// db.close((err)=>{
//     if(err){
//         return console.error(err.message);
//     }
// })

function getInformation() {
    const db = db_connection();
    
    const movies =  new Promise((resolve,reject)=>{
        db.all("select * from  movie_information",[],(err,rows)=>{
            if(err){
                
                reject(err);
            } 
            else{
                
                resolve(rows);
            } 
            db.close();
        });
    });
    return movies;
    
}

function typeHeadSearch(db, query) {
    return new Promise((resolve, reject) => {
        db.all(
            "SELECT title ratings, release_date from (SELECT DISTINCT  title, ratings, release_date FROM movie_information WHERE title LIKE ? AND ratings >= 5) ORDER BY RANDOM()  LIMIT 25  ",
            [`%${query}%`],
            (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            }
        );
    });
}

async function typeHeadSearch_postgres(query) {
  try {
    const result = await pg_pool.query(
     "SELECT title ratings, release_date from (SELECT DISTINCT  title, ratings, release_date FROM movie_information WHERE title LIKE ? AND ratings >= 5) ORDER BY RANDOM()  LIMIT 25  ",
      [`%${query}%`]
    );
    return result.rows;
  } catch (err) {
    throw err;
  }
}


function getFullMovie(db,movie_name){
    return new Promise((resolve, reject) => {
        db.all(
            "SELECT * FROM movie_information WHERE Title LIKE ? AND Ratings >= 5 ORDER by RANDOM() LIMIT 25 ",
            [`%${query}%`],
            (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            }
        );
    });
}

function specificMovie(db,movie_name){
    console.log("movie name in db = ",movie_name);
    return new Promise((resolve, reject) => {
        
        db.all(
            "SELECT * FROM movie_information WHERE Title = ? LIMIT 1 ",
            [`${movie_name}`],
            (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            }
        );
    });
}


module.exports={
    db_connection,movie_recom_table_create,InsertIntoDB,getCount,dropTable,dataCheck,tableCheck,getInformation, typeHeadSearch, specificMovie,typeHeadSearch_postgres
}

// if (require.main === module) {
//     const db = db_connection();
//     const create_table = getInformation();
//     db.close();
// }
