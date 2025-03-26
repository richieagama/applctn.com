// TaskContext to manage state across the stepper
// src/context/TaskContext.js
import React, { createContext, useContext, useState } from 'react';

const TaskContext = createContext();

export const useTaskContext = () => useContext(TaskContext);

export const TaskProvider = ({ children }) => {
  const [taskData, setTaskData] = useState({
    // Step 1: Details
    title: '',
    description: '',
    
    // Step 2: Setup
    priority: 'medium',
    dueDate: '',
    assignee: '',
    
    // Step 3: Configuration
    notifications: true,
    reminders: true,
    tags: [],
    
    // Status
    completed: false
  });
  
  const updateTaskData = (newData) => {
    setTaskData(prev => ({
      ...prev,
      ...newData
    }));
  };
  
  return (
    <TaskContext.Provider value={{ taskData, updateTaskData }}>
      {children}
    </TaskContext.Provider>
  );
};
