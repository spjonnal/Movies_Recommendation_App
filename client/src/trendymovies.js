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
            
            
            const keys = Object.keys(data); // column names
            const rowCount = data[keys[0]].length;
            console.log("trendy movies and rowCount = ",data,rowCount);// this is a dictionary {"key1":[list of values],"key2":[list of values]..}
            const structured = Array.from({ length: rowCount }, (_, i) => {
              const row = {};
              keys.forEach(key => {
                row[key] = data[key][i];
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
                        {Object.keys(resp).map((col_name) => (
                            <th key={col_name}>{col_name}</th>
                        ))}
                        </tr>
                        
                
                    </thead>
                    <tbody>
                        {resp.map((movie, index) => (
                        <tr key={index}>
                            {Object.values(movie).map((value, idx) => (
                            <td key={idx}>
                                {value}
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
