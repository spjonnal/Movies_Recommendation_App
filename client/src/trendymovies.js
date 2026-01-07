import React, { useState } from 'react';

function TrendyMovies() {
    const [resp, setResp] = useState([]);
    const [loading , setLoading] = useState(false);
    const api_base = process.env.REACT_APP_API_BASE;
    // Utility function to format column names
    const formatColumnName = (name) => {
    return name
        .replace(/_/g, " ")        // replace underscores with spaces
        .replace(/\b\w/g, (c) => c.toUpperCase()); // capitalize each word
    };

    const nodeTrendyInformation = async (event) => {
        event.preventDefault();
        try {
            setLoading(true);
            const response = await fetch(`${api_base}/api/send-trendy-movies`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            });
            if(!response.ok){
                const err_msg = await response.text();
                throw new Error(`Backend error ${response.status}:${err_msg}`);
            }
            const data = await response.json();
            console.log("trendy movies = ",data);
            
            const numMovies = data.movie_names.length;

            const structured = Array.from({ length: numMovies }, (_, i) => ({
                movie_name: data.movie_names[i],
                imdb_rating: data.imdb_rating[i],
                movie_length: data.movie_length[i],
                certificate: data.certificate[i],
                release_time: data.release_time[i],
            }));
            
            setResp(structured);

        } catch (err) {
            console.error("the error in trendy movies react code = ",err.toString());
        }
        finally{
            setLoading(false);
        }
    };
    return (
        <div>
            {
                resp.length === 0 && (
                    <button className='trendy_movies_button' onClick={nodeTrendyInformation}>Find out which movies are trending here..</button>
                )
            }
            {
                loading && (
                    <h2>We appreciate your waiting while the data is loading..</h2>
                )
            }
            
            {!loading && resp.length > 0 && (
                <table className = "trendy_movies_table">
                    <thead>
                        <tr>
                        {Object.keys(resp[0]).map((col_name, index) => (
                            <th key={index}>{formatColumnName(col_name)}</th>
                        ))}
                        </tr>
                    </thead>
                    <tbody>
                        {resp.map((movie, index) => (
                        <tr key={index}>
                            {Object.entries(movie).map(([key, value], idx) => (
                            <td key={idx}>
                                {typeof value === 'string' && value.match(/\.(jpeg|jpg|gif|png|webp)$/i) ? (
                                <img src={value} alt="movie" style={{ width: '100px', height: 'auto' }} />
                                ) : (
                                value
                                )}
                            </td>
                            ))}
                        </tr>
                        ))}
                    </tbody>
                    </table>

            )}
            
        </div>
    );
}

export default TrendyMovies;
