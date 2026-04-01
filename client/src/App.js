// export default App;
import React from 'react';
import './App.css';
import TrendyMovies from './trendymovies';
import MovieSearch from './moviesearch';

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
                        <Link to="/trendymovies">Trending Movies</Link>
                    </li>

                </ul>
            </nav>

            <Routes>
                <Route index path="/" element={<MovieSearch/>} />
                <Route  path="/trendymovies" element={<TrendyMovies />} />
            </Routes>
        </BrowserRouter>
        
    );
}

export default App;
