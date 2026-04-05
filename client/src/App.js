// export default App;
import React from 'react';
import './App.css';
import TrendyMovies from './trendymovies.js';
import MovieSearch from './moviesearch.js';

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
function App() {
    return(
        
        <BrowserRouter>
            <nav className = "navigation">
                <ul className="sidebar-links">
                    <li>
                        <Link to = "/">Movie Search</Link>
                    </li>
                    <li>
                        <Link to="/trendymovies.js">Trending Movies</Link>
                    </li>

                </ul>
            </nav>

            <Routes>
                <Route index path="/" element={<MovieSearch/>} />
                <Route  path="/trendymovies.js" element={<TrendyMovies />} />
            </Routes>
        </BrowserRouter>
        
    );
}

export default App;
