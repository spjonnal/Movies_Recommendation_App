const express = require("express");
const sql_lite = require("sqlite3").verbose()
const csv_data = require("fs")
const csv_parse = require("csv-parser")
require('dotenv').config()
const cors = require("cors")
const {PythonShell} = require("python-shell")
const  {spawn}  = require('child_process')
//express app -
const exp_app = express()
PORT = 4001
exp_app.use(cors())
exp_app.use(express.json())
const {db_connection,movie_recom_table_create,InsertIntoDB,getCount,dropTable,dataCheck,tableCheck} = require('./db_file');
//get request
exp_app.get('/',(req,res)=>{
    res.json("Welcome")
})

db = db_connection();
console.log("in index.js, the db = ",db)

movie_recom_table_create(db);
InsertIntoDB(db);
// dropTable();
// getCount()
//     .then(count => {
//         console.log("Count:", count);
//         // Do something with the count
//         if(count<=0 || isNaN(count)){
//             console.log("came inside to insert data");
//             dataCheck();
//         }
//     })
//     .catch(error => {
//         console.error("Error:", error);
//     });
// exp_app.post('/api/genredata', async (req, res) => {
//     const text = req.body;
//     console.log("received genre =", text,text.inputText,typeof(text.inputText));
//     //res.json(text);
//     // var options ={
//     //     args:[
//     //         text.inputText
//     //     ]
//     // }
//     try{
//         const py_execute = await executePython("count_vectorizer.py",[text.inputText]);
//         res.json({result:py_execute});
//     }
//     catch(error){
//         res.status(500).json({error:error})
//     }
// });
// const executePython = async (path,args)=>{
//     const arguments = args.map(arg =>arg.toString());
//     const py = spawn("python",[path,...arguments]);
//     const res = await new Promise((resolve,reject)=>{
//         let out;
//         //getting the output from python
//         py.stdout.on('data',(data)=>{
//             out = JSON.parse(data)
//         })
//         //Error Handling
//         py.stderr.on('data',(data)=>{
//             console.error(`[Python] error occured:${data}`);
//             reject(out);
//         })
//         py.on('exit',(code)=>{
//             console.error(`Code exited with code: ${code}`);
//             resolve(out);
//         });
//     });
//     return out;
// }
exp_app.post('/api/genredata', async (req, res) => {
    const text = req.body;
    console.log("received genre =", text.inputText);
    try {
        const py_execute = await executePython("count_vectorizer.py", [text.inputText]);
        const parsedOutput = JSON.parse(py_execute.toString()); // Assuming the output is in JSON format
        console.log("Received data from Python:", parsedOutput);
        res.json({ result: parsedOutput });
    } catch (error) {
        console.error("Error executing Python script:", error);
        res.status(500).json({ error: "Error executing Python script" });
    }
});

const executePython = async (path, args) => {
    const arguments = args.map(arg => arg.toString());
    const py = spawn("python", [path, ...arguments]);
    let out = "";

    // Error Handling
    py.stderr.on('data', (data) => {
        console.error(`[Python] error occurred: ${data}`);
        out += data.toString();
    });

    //Getting the output from Python
    py.stdout.on('data', (data) => {
        //console.log(`[Python] output: ${data}`);
        out += data.toString();
        console.log("output out = ",out)

    });
    return new Promise((resolve, reject) => {
        py.on('exit', (code) => {
            if (code === 0) {
                resolve(out);
            } else {
                reject(out);
            }
        });
    });
};

// exp_app.post('/api/search',(req,res)=>{
//     const db = db_connect();
//     db.serialize(()=>{

//     })
// })

exp_app.listen(process.env.PORT,()=>{
    console.log("listening on port ",process.env.PORT)
})

exp_app.post('/api/submitMovieData', (req, res) => {
    const movieData = req.body;
    console.log("received values are = ", movieData);
    const rated = movieData.Adult_Rated === true ? 1 : 0;
    db.get(`select count(*) as count from movie_information where Original_Title = ?`,movieData.movieName,(err,row)=>{
        if(row.count>1){
            console.error("Movie name '"+movieData.movieName+"'already exists in the DB",err);
            res.status(400).json({error:"Movie name already exists in the DB"});
        }
        else{
            db.run(`
            INSERT INTO movie_information(Title,ratings,release_date,runtime,genres_included,adult_rated,original_language,cast_information)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            `, [
            movieData.movieName, parseFloat(movieData.imdbRating), movieData.releaseYear,
            parseFloat(movieData.runtime), movieData.genres, rated,
            movieData.originalLanguage, movieData.castInformation
            ], (err) => {
            if (err) {
                console.error(err.message);
                res.status(500).json({ error: "Unable to insert data into database" });
            } else {
                console.log("Data inserted successfully");
                res.status(200).json({ success: true });
            }
            //db.close();
            });
        }
    })
    });




let sql = `select * from movie_information where Original_Title = 'Dune: Part One'`;

db.all(sql, [], (err, rows) => {
  if (err) {
    throw err;
  }
  console.log("select query rules = ",rows)
});


