import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import HelpPage from './pages/HelpPage';
import KeywordProcessorApp from './KeywordProcessorApp';
import { TaskProvider } from './context/TaskContext';

// Import Task Step Pages
import TaskDetailsPage from './pages/task/TaskDetailsPage';
import TaskSetupPage from './pages/task/TaskSetupPage';
import TaskConfigPage from './pages/task/TaskConfigPage';
import TaskReviewPage from './pages/task/TaskReviewPage';
import TaskSubmitPage from './pages/task/TaskSubmitPage';

function App() {
  return (
    <div className="App">
      <Navigation />
      <TaskProvider>
        <Routes>
          <Route path="/" element={<KeywordProcessorApp />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/help" element={<HelpPage />} />
          
          {/* Task Stepper Routes */}
          <Route path="/task/details" element={<TaskDetailsPage />} />
          <Route path="/task/setup" element={<TaskSetupPage />} />
          <Route path="/task/config" element={<TaskConfigPage />} />
          <Route path="/task/review" element={<TaskReviewPage />} />
          <Route path="/task/submit" element={<TaskSubmitPage />} />
        </Routes>
      </TaskProvider>
    </div>
  );
}

export default App;