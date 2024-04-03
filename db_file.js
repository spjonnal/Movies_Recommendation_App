const sqdb = require("sqlite3").verbose()
const csv_data = require("fs")
const csv_parse = require("csv-parser")

function db_connection(){
    const db = new sqdb.Database("sqdb.db",sqdb.OPEN_READWRITE,(err)=>{
        if(err){
            console.error(err.message)
        }
        else{
            console.log("DB connnection successful!")
        }
    })
    return db
}
// function db_connection() {
//     return new Promise((resolve, reject) => {
//         const db = new sqdb.Database("sqdb.db", sqdb.OPEN_READWRITE, (err) => {
//             if (err) {
//                 reject(err); // Reject the promise if there's an error
//             } else {
//                 console.log("DB connection successful!");
//                 resolve(db); // Resolve the promise with the database object
//             }
//         });
//     });
// }

function movie_recom_table_create(db){
    console.log("came to create a table",db)
    db.get("SELECT name FROM sqlite_master WHERE type = 'table' and name = 'movie_information'",(err,row)=>{
        console.log("errpr on creation",err)
        if(err){
            console.error("Some error more information ->",err.message);
        }
        if (row){
            console.log("Table movie_information already exists",row);
        }
        else{
            db.run(`CREATE TABLE IF NOT EXISTS movie_information(
                Adult_Rated boolean,
                Genres VARCHAR(150),
                Movie_id integer,
                IMDB_ID integer,
                Original_Language VARCHAR(20),
                Original_Title VARCHAR(75),
                Overview VARCHAR(1000),
                Popularity real,
                Release_Date VARCHAR(25),
                Runtime real,
                Spoken_Languages VARCHAR(250),
                Tagline VARCHAR(1000),
                Title VARCHAR(100),
                Vote_Average real,
                vote_count real,
                Genres_Included VARCHAR(250),
                ratings varchar(10),
                Cast_Information VARCHAR(1500))`,(err)=>{
                if(err){
                    console.error("error thrown in movie data info table creation ->",err.message);
                }
                else{
                    console.log("Table movie_information created successfully");
                    
                }
            });
        }
    });
    
}

function dropTable() {
    db = db_connection();
    db.run(`DROP TABLE IF EXISTS movie_information`, (err) => {
        if (err) {
            console.error('Error dropping table:', err.message);
        } else {
            console.log('Table dropped successfully.');
            // Once the table is dropped, start reading and inserting data
            //readAndInsertData();
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
// function InsertIntoDB() {
//     db = db_connection();
//     // movie_recom_table_create(db)
//     const data_result = [];
//     csv_data.createReadStream('C:\\University_of_Waterloo\\winter 2024\\Django_Project\\Node_React_Movie_App\\Movie_Final_Modified.csv')
//         .pipe(csv_parse({}))
//         .on('data', (data) => data_result.push(data))
//         .on('end', () => {
//             console.log("CSV data read successfully.",typeof(data_result),data_result.length);
//     });
//     //console.log("CSV data in results individual columns", data_result[0]['adult']);
//     for (let i = 0; i < data_result.length; i++) {
//         // const Adult_Rated = data_result[i]["adult"] === 'true' ? 1 : 0;
//         // const mov_id = parseInt(data_result[i]["id"])
//         // const IMDB_ID = parseInt(data_result[i]["imdb_id"])
//         // const Popularity = parseFloat(data_result[i]["popularity"]);
//         // //const Release_Date = new Date(data_result[i]["release_date"]);
//         // const Runtime = parseFloat(data_result[i]["runtime"]);
//         // const Vote_Average = parseFloat(data_result[i]["vote_average"]);
//         console.log("came into the for loop and inserting the data");
//         const movie_ratings = parseFloat(data_result[i]["rating"]);
//         db.run(`INSERT INTO movie_information (
//             Adult_Rated, Genres,Movie_id, IMDB_ID, Original_Language, Original_Title,
//             Overview, Popularity, Release_Date, Runtime, Spoken_Languages,
//             Tagline, Title, Vote_Average, vote_count, Genres_Included, Cast_Information,ratings
//             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)`,
//             [
//                 data_result[i]["adult"], data_result[i]["genres"], data_result[i]["id"], data_result[i]["imdb_id"], data_result[i]["original_language"], data_result[i]["original_title"],
//                 data_result[i]["overview"], data_result[i]["popularity"], data_result[i]["release_date"], data_result[i]["runtime"], data_result[i]["spoken_languages"],
//                 data_result[i]["tagline"], data_result[i]["title"], data_result[i]["vote_average"], data_result[i]["vote_count"], data_result[i]["genres_included"],
//                 data_result[i]["cast_info_complete"],movie_ratings
//             ],
//             function Problem(err) {
//                 if (err) {
//                     return console.error(err.message);
//                 } else {
//                     console.log("Successful insertion into DB");
//                 }
//             }
//         );
//     }
// }
function InsertIntoDB(db){
    db.get("SELECT COUNT(*) AS count from movie_information",(err,row)=>{
        const count = row ? row.count : 0;
        if(err){
            console.error("Some error while checking the data count in the db.js file. Mode details ->",err.message);
        }
        else if(count <1){
            console.log("No data exists. Inserting data",count);
            const data_result = [];
            csv_data.createReadStream('C:\\University_of_Waterloo\\winter 2024\\Django_Project\\Node_React_Movie_App\\Movie_Final_Modified.csv')
                .pipe(csv_parse({}))
                .on('data', (data) => data_result.push(data))
                .on('end', () => {
                    console.log("CSV data read successfully.", typeof (data_result), data_result.length);
                    // db.then(db => {
                    //     console.log("Database connection established.");
                        for (let i = 0; i < data_result.length; i++) {
                            const movie_ratings = parseFloat(data_result[i]["rating"]);
                            const ad_rat = data_result[i]['adult'] === '1'? true : false;
                            const mov_id  = parseInt(data_result[i]["id"]);
                            const imdb_id = parseInt(data_result[i]["imdb_id"]);
                            const popularity = parseFloat(data_result[i]["popularity"]);
                            const mov_len = parseFloat(data_result[i]["runtime"]);
                            const vote_average = parseFloat(data_result[i]["vote_average"]);
                            const vote_count = parseFloat(data_result[i]["vote_count"]);
                            db.run(`INSERT INTO movie_information (
                                Adult_Rated, Genres, Movie_id, IMDB_ID, Original_Language, Original_Title,
                                Overview, Popularity, Release_Date, Runtime, Spoken_Languages,
                                Tagline, Title, Vote_Average, vote_count, Genres_Included, Cast_Information, ratings
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                                [
                                    ad_rat, data_result[i]["genres"], mov_id, imdb_id, data_result[i]["original_language"], data_result[i]["original_title"],
                                    data_result[i]["overview"], popularity, data_result[i]["release_date"], mov_len, data_result[i]["spoken_languages"],
                                    data_result[i]["tagline"], data_result[i]["title"], vote_average, vote_count, data_result[i]["genres_included"],
                                    data_result[i]["cast_info_complete"], movie_ratings
                                ],
                                function Problem(err) {
                                    if (err) {
                                        return console.error("Some error in insertion. More information ->",err.message);
                                    } else {
                                        console.log("Successful insertion into DB");
                                    }
                                }
                            );
                        }
                    // }).catch(error => {
                    //     console.error("Error establishing database connection:", error.message);
                    // });
                });
        }
        else{
            console.log("Data Already Exists in the table");
        }
    
    });
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

module.exports={
    db_connection,movie_recom_table_create,InsertIntoDB,getCount,dropTable,dataCheck,tableCheck
}
// db = db_connection();
// db.run(`
// create table movie_information(
//     ID integer PRIMARY KEY AUTOINCREMENT,
//     Adult_Rated boolean,
//     Genres VARCHAR(150),
//     Movie_id integer,
//     IMDB_ID integer,
//     Original_Language VARCHAR(20),
//     Original_Title VARCHAR(75),
//     Overview VARCHAR(1000),
//     Popularity real,
//     Release_Date DATE,
//     Runtime real,
//     Spoken_Languages VARCHAR(250),
//     Tagline VARCHAR(1000),
//     Title VARCHAR(100),
//     Vote_Average real,
//     vote_count real,
//     Genres_Included VARCHAR(250),
//     Cast_Information VARCHAR(1500)
// )
// `);
