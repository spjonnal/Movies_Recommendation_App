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
            
            
            //const keys = Object.keys(data); // column names
            //const rowCount = data?.["Movie Name"].length || [];
            //console.log("trendy movies and rowCount = ",data,rowCount);// this is a dictionary {"key1":[list of values],"key2":[list of values]..}
            // Convert each movie object to a structured object with readable keys
            const structured = data.map(movie => {
                const row = {};
                Object.entries(movie).forEach(([key, value]) => {
                    row[formatColumnName(key)] = value;
                });
                return row;
            });

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
                        {Object.keys(resp[0]).map((col_name) => (
                            <th key={col_name}>{col_name}</th>
                        ))}
                        </tr>
                        
                
                    </thead>
                    <tbody>
                        {resp.map((row, rowIndex) => (
                            <tr key={rowIndex}>
                            {Object.entries(row).map(([key, value], idx) => (
                                <td key={idx}>
                                {key === "Image Url" ? (
                                    <img src={value} alt="movie" style={{ width: "100px", height: "auto" }} />
                                ) : key === "Imdb Url Page" ? (
                                    <a href={value} target="_blank" rel="noopener noreferrer">
                                    View on IMDB
                                    </a>
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
