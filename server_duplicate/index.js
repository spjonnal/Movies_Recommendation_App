
import express from "express";
import cors from "cors";


const app = express();
import {spawn} from "child_process";
import json from "stream/consumers";
import resolve from "path";
import rejects from "assert";
import error from "console";
import fs from "fs";
import fast_csv from "fast-csv";
import {CloudClient} from "chromadb";
import OPENAI from "openai";
import axios from "axios";
import 'dotenv/config';
//const {spawn} = require("child_process");

// const { json } = require("stream/consumers");
// const { resolve } = require("path");
// const { rejects } = require("assert");
// const { error } = require("console");
// const fs = require("fs");
// const fast_csv = require("fast-csv");

// const CloudClient  = require('chromaDB')
// const OPENAI = require('openai');

import {db_connection,movie_recom_table_create,InsertIntoDB,getCount,dropTable,dataCheck,tableCheck,getInformation,
  typeHeadSearch, specificMovie
} from './db_file.cjs';
import { type } from "os";


const PORT = process.env.PORT || 4000;

app.use(express.json())
app.use(cors());

// const openai = new OPENAI({
//   apiKey: process.env.OPENAIKEY
  
// });



const COLLECTION_NAME = "movie_recommendation_system";



app.get('/send_data_to_vectorDB', async (req, res) => {
    try {
        const movies_table = await getInformation();

        console.log("movies from db to vector db = ", movies_table);
        res.json(movies_table);
    } catch (err) {
        console.error("Error fetching data:", err);
        res.status(500).json({ error: "Failed to fetch movies" });
    }
});


app.get("/", (req, res) => {
    
    res.json("Welcome");
  });

app.post('/api/send-genre',async (req,res)=>{
    try{

    const genre = req.body;//get the genre
    
    const py_output = await executePython('count_vectorizer.py',[JSON.stringify(genre.inputText)]); // send to python for execution
    const parsedOut = JSON.parse(py_output.toString()); // response
    res.json({parsedOut});
    
    }
    catch(err){
        console.log("error in post = ",err.toString());
    }
});

app.post('/api/typehead',async(req,res)=>{
  try{
    const {inputText} = req.body;
    const db = db_connection();
    
    const return_data = await new typeHeadSearch(db,inputText);
    console.log("input data from db  =",return_data)
    res.json({return_data});
  }
  catch(err){
    console.error("some error in the type head node code",err.toString());
  }
})

app.post('/api/movieinfo',async(req,res)=>{
  try{
    const movie_name = req.body;
    
    const db = db_connection();
    const complete_movie_info = await specificMovie(db,movie_name.selected_movie);
    
    res.json({complete_movie_info});
  }
  catch(err){
    console.error("some error in db while getting movie info = ",err.toString());
  }
})

const executePython = (path, args) => {
    return new Promise((resolve, reject) => {
        const py_call = spawn("python", [path, args]);
        let py_out = '';
        let error_output = '';

        py_call.stdout.on('data', (py_data) => {
            py_out += py_data;
        });

        py_call.stderr.on('data', (err) => {
            error_output += err;
        });

        py_call.on('close', (code) => {
            if (code !== 0) {
                reject(`Python script exited with code ${code}. Error: ${error_output}`);
            } else {
                resolve(py_out);
            }
        });
    });
};

const getTrendingMovies = (path) => {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [path]);
    let dataString = '';
    let error_out = '';

    pythonProcess.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    pythonProcess.stderr.on('data', (err) => {
      error_out += err.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(`Python exited with code ${code}. Error: ${error_out}`);
      } else {
        try {
          const parsed = JSON.parse(dataString); 
          resolve(parsed);
        } catch (err) {
          reject(`Invalid JSON from Python: ${dataString}\nError: ${err}`);
        }
      }
    });
  });
};

app.post('/api/send-trendy-movies', async (req, res) => {
  try {
    const return_data_trendy = await getTrendingMovies('web_scraping.py');
    res.json(return_data_trendy);
    
  }
  catch(err){
    console.error("error in web scraping = ",err.error);
  }
});


app.post("/api/ask_llm", async (req, res) => {
  
  try {
    const question = (req.body && req.body.question)
    
    const response = await axios.post(
      "http://127.0.0.1:8000/ask_llm",
      { question },
      { headers: { "Content-Type": "application/json" } }
    );

    

    res.json(response.data); // IMPORTANT FIX
  } 
  catch (e) {
    console.error("some error:", e.toString());
    res.status(500).json({ error: "Backend error", details: e.toString() });
  }
});

app.listen(PORT, () => {
  console.log(`Example app listening on port ${PORT}`)
})

