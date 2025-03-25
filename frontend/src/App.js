import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import HelpPage from './pages/HelpPage';
import KeywordProcessorApp from './KeywordProcessorApp'; // Rename your current App component to KeywordProcessorApp

function App() {
  return (
    <div className="App">
      <Navigation />
      <Routes>
        <Route path="/" element={<KeywordProcessorApp />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/help" element={<HelpPage />} />
      </Routes>
    </div>
  );
}

export default App;