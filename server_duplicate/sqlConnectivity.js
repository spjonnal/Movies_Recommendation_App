// const sql_lite = require("sqlite3").verbose()
// const db = new sql_lite.Database("sqdb.db",sql_lite.OPEN_READWRITE,(err)=>{
//     if(err){
//         console.error(err.message)
//     }
//     else{
//         console.log("DB connnection successful!")
//     }
// })

// function createTable(db){
//     db.exec(`
//     create table movie_information(
//         Movie_Id int primary key not null,
//         Adult_Rated boolean not null,
//         Genres text not null,
//         IMDB_ID integer,
//         Original_Language text not null,
//         Original_Title text not null,
//         Overview text not null,
//         Popularity real,
//         Release_Date DATE,
//         Runtime real,
//         Spoken_Languages text not null,
//         Tagline text,
//         Title text not null,
//         Vote_Average real,
//         vote_count real,
//         Genres_Included text not null,
//         Cast_Information text
//     );
//     `)

// }
// function readCSVFile(db) {
//     const results = [];
//     fs.createReadStream('C:\\University_of_Waterloo\\Fall_2023\\Django_Project\\Node_React_Movie_App\\movies_final_data.csv')
//         .pipe(csv())
//         .on('data', (data) => results.push(data))
//         .on('end', () => {
//             // Insert data into the table
//             results.forEach((row) => {
//                 const releaseDate = new Date(row.Release_Date);
//                 const adultRated = row.Adult_Rated === 'true' ? true : false;
//                 const prim_key = parseInt(row.Movie_ID);
//                 const rating_imdb = parseInt(row.IMDB_ID);
//                 const popul = parseFloat(row.Popularity);
//                 const mov_length = parseFloat(row.Runtime);
//                 const average_voting = parseFloat(row.Vote_Average);
//                 const average_count = parseFloat(row.Vote_Count)
//                 db.run(`
//                     INSERT INTO movie_information (
//                         Movie_Id,Adult_Rated, Genres, IMDB_ID, Original_Language, Original_Title,
//                         Overview, Popularity, Release_Date, Runtime, Spoken_Languages,
//                         Tagline, Title, Vote_Average, Vote_Count, Genres_Included, Cast_Information
//                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
//                 `, [
//                     prim_key,adultRated, row.Genres, rating_imdb, row.Original_Language, row.Original_Title,
//                     row.Overview, popul, releaseDate, mov_length, row.Spoken_Languages,
//                     row.Tagline, row.Title, average_voting, average_count, row.Genres_Included, row.Cast_Information
//                 ], (err) => {
//                     if (err) {
//                         console.error('Error inserting data:', err.message);
//                     } else {
//                         console.log('Data inserted successfully.');
//                     }
//                 });
//             });
//             closeDBConnection(db); // Close the database connection after data insertion
//         });
// } 

// function closeDBConnection(db) {
//     db.close((err) => {
//         if (err) {
//             console.error(err.message);
//         } else {
//             console.log('Connection to the database closed.');
//         }
//     });
// }

// module.exports = { ConnectToDB,createTable, closeDBConnection };