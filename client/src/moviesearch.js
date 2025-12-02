import React, {  useState } from 'react';

import SelectGenre from './resue_select_genre';
import Chatbotlogic from './chatbotlogic';
import './App.css'
// import { data } from 'react-router-dom';



function MovieSearch(){
      // const [movie_genre, setMovieGenre] = useState('');
    const [resp, setResp] = useState([]);
    const [selectedGenre, setSelectedGenre] = useState('');
    const [contribute, setContribute] = useState(false);
    const [sortkey, setSortKey] = useState("")
    const [loading, setLoading] = useState(false);
    const [typeHead, setTypeHead] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [movie_info, setMovieInfo] = useState([]);
    

    const handleCheckBoxChange = (chgeEvent) => {
        setContribute(chgeEvent.target.checked);
    };

    const handleGenreSelection = (event)=>{
        
        setSelectedGenre(event.value);
        
    };

    const handleTypeHead = async (event) => {
        const inputText = event.target.value;
        
        setTypeHead(inputText);

        if (inputText.length < 2) {
            setSuggestions([]);
            return;
        }

        try {
            const response = await fetch("http://localhost:4001/api/typehead", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ inputText }),
            });

            const data = await response.json();

            setSuggestions(data.return_data || []);
        } catch (err) {
            console.error("React fetch error:", err);
        }
    };

    const handleMovieClick = async (title)=>{
        
        const selected_movie = title;
        console.log("selected movie name = ",selected_movie);
        try{
            const movie_complete_info = await fetch("http://localhost:4001/api/movieinfo",{
                method :"POST",
                headers:{
                    "Content-Type": "application/json"
                },
                body:JSON.stringify({selected_movie}),
            });
            const return_data = await movie_complete_info.json();
            
            setMovieInfo(return_data.complete_movie_info);
        }
        catch(err){
            console.error("some issue in retrieving the movie information in react = ",err.toString());
        }
    }


    const sendData = async (event) => {
        event.preventDefault(); // prevent page reload
        
        if(selectedGenre !== "" && selectedGenre !== "--Please Select--" ){

        
            try {
                setLoading(true);
                const response = await fetch("http://localhost:4001/api/send-genre", {
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
            }
        }
        else{
            alert("Please select a valid genre");
        }   
    };

    const displayGrace = (event) => {
        event.preventDefault();
        alert("Movie data submitted! (You can now link this to a backend)");
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
                    <h1>Welcome to Mowickie... One stop destination for best movie recommendations!</h1>
                   
                    
                    <SelectGenre onChange = {handleGenreSelection} value={selectedGenre}></SelectGenre>
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
                                            <li onClick={()=>handleMovieClick(value.Title)} key={ind}>{value.Title},&nbsp;&nbsp;{value.Ratings}</li>
                                            
                                        );
                                    })}
                                </ul>
                            )
                        }
                   </div>
                    <button id = "submit_button" type='submit'>Submit</button>
                </form>
                {movie_info.length > 0 && (
                    <table >
                        <thead>
                            <tr>
                                {Object.keys(movie_info[0]).map((col_name, key) => (
                                    <th key={key}>{col_name}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {movie_info.map((mov, ind) => (
                                <tr key={ind}>
                                    {Object.entries(mov).map(([key,val], i) => (
                                        <td key={i}>{
                                            key.toLowerCase().includes("url") && typeof val ==="string" && val.startsWith("http")?
                                            ( <a href={val} target="_blank" rel="noreferrer">{val}</a>  ):(val)
                                            }
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
                {
                    loading && (
                        <h2>We appreciate your waiting while the data is loading..</h2>
                    )
                }
                {
                    !loading && resp.length>0 && (
                    <div>
                        <select onChange ={(e)=>setSortKey(e.target.value)}>
                            <option value="">--select--</option>
                            <option value="Ratings">IMDB Ratings</option>
                            <option value="Release Date">Release Date</option>
                        </select>
                    </div>
                    )
                }
                {sorting.length > 0 && (
                    <table >
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
                                            key.toLowerCase().includes("url") && typeof val ==="string" && val.startsWith("http")?
                                            ( <a href={val} target="_blank" rel="noreferrer">{val}</a>  ):(val)
                                            }
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
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
                            <label htmlFor = 'movie_name'> Enter movie/series name here : 
                            <input type='text' name = 'movie_name' placeholder='Movie/Series name' id = 'movie_name' required /> 
                            </label>
                            <br /> 
                            <label htmlFor = 'movie_duration'>Enter the movie duration here :
                            <input type="text" name='movie_duration' inputMode="decimal" pattern="[0-9]*[.,]?[0-9]*" placeholder='Duration (minutes)' id = 'movie_duration' required />
                            </label>
                            <br />
                            <label htmlFor = 'imdb rating'>Enter the IMDB ratings of the movie here :
                            <input type='text' name='imdb rating' placeholder='IMDB Ratings' id = 'imdb rating'required />
                            </label>
                            <br />
                            <label htmlFor = 'language'>Enter the original language of the movie here :
                            <input type='text' name='language' placeholder='Original Language' id ='language' required />
                            </label>
                            <br />
                            <label htmlFor = 'cast and crew'>Enter cast and crew inhtmlFormation here :
                            <input type='text' name = 'cast and crew' placeholder='Cast & Crew Info' id ='cast and crew' />
                            </label>
                            <br />
                            <label htmlFor='certificates' className='censorship_dropdown'>Select the censorship of the movie:</label>
                            <select name='certificates' id = 'certificates' >
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
                            <label htmlFor = 'genres' className='genre_design'>Select the movie genre from below :</label>
                            <SelectGenre name='genres' id= 'genres' onSubmit></SelectGenre>
                            <p>*Hold down the Ctrl (windows) or Command (Mac) button to select multiple options.</p>
                            <br/>
                            <label htmlFor = 'dubbing'>Enter all langauges in which the moies is available here :</label>
                            <input type='text' name  = 'dubbing' placeholder='Dubbed Languages' id = 'dubbing' />
                            <br />
                            <button id = "submit_button" type='submit'>Submit Your Movie</button>
                        </div>
                        
                    </form>
                )}
        </div>
        
    );
}

export default MovieSearch;