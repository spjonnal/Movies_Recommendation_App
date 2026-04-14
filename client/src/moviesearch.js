import React, {  useState } from 'react';

import SelectGenre from './resue_select_genre.js';
import Chatbotlogic from './chatbotlogic.js';

import './App.css'
// import { data } from 'react-router-dom'

function MovieSearch(){
      // const [movie_genre, setMovieGenre] = useState('');
    const [resp, setResp] = useState([]);
    const [selectedGenre, setSelectedGenre] = useState('');
    const [contribute, setContribute] = useState(false);
    const [sortkey, setSortKey] = useState("")
    const [loading, setLoading] = useState(false);
    const[closeGenreSelectData,setCloseGenreSelectData] = useState(false);
    const [closeDataInfo, setCloseDataInfo] = useState(false);
    const [closeTypeHeadDataInfo, setCloseTypeHeadDataInfo] = useState(false);
    const [typeHead, setTypeHead] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const api_base = process.env.REACT_APP_API_BASE;
    const [movie_info, setMovieInfo] = useState([]);
    const [postMovieData, setPostMovieData] = useState({
        movie_name: "",
        release_date:"",
        movie_duration: "",
        imdb_rating: "",
        language: "",
        cast_and_crew: "",
        certificates: "def",
        genres: [],
        dubbing: "",
    });
    
    

    const handleCheckBoxChange = (chgeEvent) => {
        setContribute(chgeEvent.target.checked);
    };

    const handleSetCloseMovieInfo = ()=> setCloseDataInfo(!closeDataInfo);
    const handleSetCloseTypeHeadMovieInfo = ()=>setCloseTypeHeadDataInfo(!closeTypeHeadDataInfo);

    const handleGenreSelection = (event)=>{
        
        setSelectedGenre(event.value);
        
    };
    const handleCloseGenreSelectData = ()=>setCloseGenreSelectData(!closeGenreSelectData);

    const handleContributedGenreSelection = (event)=>{
        setPostMovieData({...postMovieData,genres:event.value,});
    }

    const handleContributedRestData = (e)=>{
        setPostMovieData({
            ...postMovieData,[e.target.name]: e.target.value,
        });
    };

    const handleTypeHead = async (event) => {
        const inputText = event.target.value;
        
        setTypeHead(inputText);

        if (inputText.length <=1) {
            setSuggestions([]);
            return;
        }

        try {
            const response = await fetch(`${api_base}/api/typehead`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ inputText }),
            });

            const data = await response.json();
            
            setSuggestions(
                (data.return_data && data.return_data.length>0)? data.return_data : [{title:"Movie information not found..😰",ratings:""}]
            );
        } catch (err) {
            console.error("React fetch error:", err);
        }
    };

    const handleMovieClick = async (title)=>{
        
        const selected_movie = title;
        
        try{
            const movie_complete_info = await fetch(`${api_base}/api/movieinfo`,{
                method :"POST",
                headers:{
                    "Content-Type": "application/json"
                },
                body:JSON.stringify({selected_movie}),
            });
            const return_data = await movie_complete_info.json();
            
            setMovieInfo(return_data);
        }
        catch(err){
            console.error("some issue in retrieving the movie information in react = ",err.toString());
        }
        finally{
            setCloseDataInfo(false);
        }
    }


    const sendData = async (event) => {
        event.preventDefault(); // prevent page reload
        
        if(selectedGenre !== "" && selectedGenre !== "--Please Select--" ){

        
            try {
                setLoading(true);
                const response = await fetch(`${api_base}/api/send-genre`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ inputText: selectedGenre })
                    
                    
                });
                const data = await response.json();
                
                setResp(data.parsedOut);
                
            } catch (error) {
                alert(error.toString());
            }
            finally{
                setLoading(false); // for displaying a loading message
                setCloseDataInfo(false);
            }
        }
        else{
            alert("Please select a valid genre");
        }   
    };

    const displayGrace = async (event) => {
        event.preventDefault();
        try{
            
            
        
            const send_contribution_data = await fetch(`${api_base}/api/send-contribution-data`,{
                method:"POST",
                headers:{
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(postMovieData )
            })
              
            const data = await send_contribution_data.json();
            
            if(data.success){
                alert("Data inserted. We appreciate your contribution..");
            }
        }
        catch(error){
            console.log("some error while storing your information",error.toString());
    
        }
    
        
    };
    const sorting = [...resp].sort((a,b)=>{
        if(!sortkey){
            return 0; // no sorting
        }
        else if(sortkey === "Ratings"){
            return parseFloat(b[sortkey]) - parseFloat(a[sortkey]); // descending order of IMDB ID
        }
        else if(sortkey === "Release Date"){
        
            const yearA = parseInt(a[sortkey].slice(0,4),10);
            const yearB = parseInt(b[sortkey].slice(0,4),10);
            return yearB-yearA; // descending order of release date
        }
        return 0;
        
    })
    return (
        <div className = "container">
                
                <form onSubmit={sendData}>
                    <br/>
                    <title>Mowickie 🎬</title>
                    <h1>Welcome to Mowickie... One stop destination for best movie recommendations!</h1>
                   
                    
                    <SelectGenre onChange = {handleGenreSelection} value={selectedGenre} id = "fav_genre_select"></SelectGenre>
                    <br /><br />
                    <div>
                        <label htmlFor='typehead'></label>
                        <input 
                            id="typehead"  
                            type="text" 
                            
                            name="typehead" 
                            placeholder="🔍 Enter the choice of your movie here" 
                            onChange={handleTypeHead}
                            value={typeHead}
                            
                             
                        />
                        {
                            suggestions.length>0 && typeHead &&  (
                                <ul id='typeheadbackground'>
                                    {suggestions.map((value,ind)=>{
                                        return (
                                            <li onMouseDown={(e)=> {e.preventDefault(); handleMovieClick(value);}} key={ind}>{value.title}&nbsp;&nbsp;{value.ratings}</li>
                                            // using onMouseDown event instead of onClick as we are trying to overcome the input loosing focus case
                                        );
                                    })}
                                </ul>
                            )
                        }
                   </div>
                    <button id = "submit_button" type='submit'>Submit</button>
                </form>
                {movie_info.complete_movie_info && movie_info.complete_movie_info.length > 0 && !closeDataInfo && (
                    <>
                        <button type="button" id="cancel_movie_data" onClick={handleSetCloseMovieInfo}>X</button>
                        {movie_info?.complete_movie_info?.map((movie, index) => (
                            <div key={index} className="movie-card">

                                {/* Top row */}
                                <div className="movie-header">
                                <h2>{movie.title}</h2>

                                <div className="movie-meta">
                                    <span>⭐ {movie.ratings}</span>
                                    <span>{movie.genres}</span>
                                    <span>{movie.runtime}</span>
                                    <span>{new Date(movie.release_date).toISOString().split('T')[0]}</span>
                                </div>
                                </div>

                                {/* Overview */}
                                <div className="movie-section">
                                <h3>Overview</h3>
                                <p>{movie.overview}</p>
                                </div>

                                {/* Cast */}
                                {movie.cast_and_crew && (
                                <div className="movie-section">
                                    <h3>Cast & Crew</h3>
                                    <p>{movie.cast_and_crew}</p>
                                </div>
                                )}

                                {/* Trailer */}
                                {movie.youtube_trailer_link && (
                                <div className="movie-section">
                                    <h3>Trailer</h3>
                                    <a href={movie.youtube_trailer_link} target="_blank" rel="noopener noreferrer">
                                    Watch on YouTube
                                    </a>
                                </div>
                                )}

                            </div>
                        ))}
                    </>
                )}
                {
                    loading && (
                        <h2>We appreciate your waiting while the data is loading..</h2>
                    )
                }
                {
                    !loading && resp.length>0 && (
                        !closeDataInfo &&(
                            <div >
                                <select onChange ={(e)=>setSortKey(e.target.value)} id='sort_genre_data'>
                                    <option value="">--select--</option>
                                    <option value="Ratings">IMDB Ratings</option>
                                    <option value="Release Date">Release Date</option>
                                </select>
                            </div>
                        )
                    )
                }
                {sorting.length > 0 && (
                    !closeDataInfo && (
                        <>
                        <button type='button' id = 'cancel_movie_data' onClick={handleSetCloseMovieInfo}>X</button>
                        {
                            sorting.map((movie,index)=>(
                                <div key={index} className = "movie-card">
                                    <div className = "movie-header">
                                    <h2>{movie['Title']}</h2>
                                    <div className = "movie-meta">
                                        <span>{movie['Ratings']}</span>
                                        <span>{movie['Gernes']}</span>
                                        <span>{movie['Runtime']}</span>
                                        <span>{new Date(movie['Release Date']).toISOString().split('T')[0]}</span>
                                    </div>
                                    </div>
                                    <div className = "movie-section">
                                        <h3>Overview</h3>
                                        <span>{movie['Overview']}</span>
                                        <h3>Cast and Crew</h3>
                                        <span>{movie['Cast and Crew']}</span>
                                        <a href = {movie['Youtube Trailer Link']} target = "_blank" without rel="noreferrer">Watch on YouTube</a>
                                    </div>
                                </div>
                                
                            ))
                        }
                        {/* <table >
                            <thead>
                                <tr>
                                    {Object.keys(sorting[0]).map((col_name, key) => (
                                        <th key={key}>{col_name}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {sorting.map((mov, ind) => (
                                    
                                        
                                            
                                    <tr key={ind}>
                                        {Object.entries(mov).map(([key,val], i) => (
                                            <td key={i}>{
                                                key.toLowerCase().includes("link") && typeof val ==="string" && val.startsWith("https")?
                                                key.toLowerCase().includes("link") && typeof val ==="string" && val.startsWith("https")?
                                                ( <a href={val} target="_blank" rel="noreferrer">{val}</a>  ):(val)
                                                }
                                            </td>
                                        ))}
                                    </tr>
                                        
                                    
                                ))}
                            </tbody>
                        </table> */}
                        </>
                    )
                )}
                <br/>
                <br/>
                <Chatbotlogic>Mowickie</Chatbotlogic>

                
                <label htmlFor = 'contribute' className='checkbox_contribute'>Want to contribute to out dataset?
                    <input type='checkbox' name='contribute' onChange={handleCheckBoxChange} className='checkbox_size'/>
                    
                </label>
                <br/>
                <br/>
                {contribute && (
                    <form onSubmit={displayGrace}>
                        <br />
                        <div className='grid_display'>
                            <label htmlFor = 'movie_name' id = "contribution_fields">Enter movie/series name here: 
                            <input type='text' name = 'movie_name' placeholder='Movie/Series name' id = 'movie_name' required onChange={handleContributedRestData} /> 
                            </label>
                            <br /> 
                            <label htmlFor = 'release_date' id = "contribution_fields">Enter/select movie release date : 
                            <input type='date' name = 'release_date' placeholder='select release date' id = 'release_date' required onChange={handleContributedRestData} /> 
                            </label>
                            <br/>
                            <label htmlFor = 'movie_duration' id = "contribution_fields">Enter the movie duration here :
                            <input type="text" name='movie_duration' inputMode="decimal" pattern="[0-9]*[.,]?[0-9]*" placeholder='Duration (minutes)' id = 'movie_duration' required 
                                onChange={handleContributedRestData}
                            />
                            </label>
                            <br />
                            <label htmlFor = 'imdb rating' id = "contribution_fields">Enter the IMDB ratings of the movie here :
                            <input type='text' name='imdb_rating' placeholder='IMDB Ratings' id = 'imdb_rating'required onChange={handleContributedRestData}/>
                            </label>
                            <br />
                            <label htmlFor = 'language' id = "contribution_fields">Enter the original language of the movie here :
                            <input type='text' name='language' placeholder='Original Language' id ='language' required onChange={handleContributedRestData}/>
                            </label>
                            <br />
                            <label htmlFor = 'cast and crew' id = "contribution_fields">Enter cast and crew inhtmlFormation here :
                            <input type='text' name = 'cast_and_crew' placeholder='Cast & Crew Info' id ='cast_and_crew' onChange={handleContributedRestData}/>
                            </label>
                            <br />
                            <label htmlFor='certificates' className='censorship_dropdown' id = "contribution_fields">Select the censorship of the movie:</label>
                            <select name='certificates' id = 'certificates' onChange={handleContributedRestData} >
                                <option value='def'>-- Please Select --</option>
                                <option value='U'>Universal Rating (U)</option>
                                <option value='U/A'>Universal with Parental Guidance (U/A)</option>
                                <option value='PG'>Parental Guidance (PG)</option>
                                <option value='PG-13'>Parental Guidance, 13+ (PG-13)</option>
                                <option value='R'>Restricted (R)</option>
                                <option value='18+'>18+ only</option>
                                <option value='A'>Adults</option>
                                <option value='S'>Restricted to special categories (S)</option>
                                <option value='NC-17'>No one under 17 (NC-17)</option>
                                <option value='Nota'>None of the above</option>
                            </select>
                            <br />
                            <label htmlFor = 'genres' className='genre_design' id = "contribution_fields">Select the movie genre from below :</label>
                            <SelectGenre name='genres' id= 'genres' onSubmit onChange={handleContributedGenreSelection}></SelectGenre>
                            <p>*Hold down the Ctrl (windows) or Command (Mac) button to select multiple options.</p>
                            <br/>
                            <label htmlFor = 'dubbing'  id = "contribution_fields"> Enter all langauges in which the moies is available here :</label>
                            <input type='text' name  = 'dubbing' placeholder='Dubbed Languages' id = 'dubbing' onChange={handleContributedRestData}/>
                            <br />
                            <button id = "submit_button" type='submit'><p id = "contribution_fields">Submit Your Movie</p></button>
                        </div>
                        
                    </form>
                )}
        </div>
        
    );
}

export default MovieSearch;
