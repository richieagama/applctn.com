// src/pages/task/TaskSubmitPage.js
import React, { useState } from 'react';
import { Typography, Button, CircularProgress, Box, Alert } from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import TaskStepper from '../../components/TaskStepper';
import { useNavigate } from 'react-router-dom';

const TaskSubmitPage = () => {
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In a real application, you would post to your API
      // const response = await fetch('/api/tasks', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(taskData)
      // });
      
      // if (!response.ok) throw new Error('Failed to create task');
      
      setSubmitted(true);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoToTasks = () => {
    navigate('/');
  };

  return (
    <TaskStepper>
      <Typography variant="h5" gutterBottom>
        Submit Task
      </Typography>
      
      {!submitted ? (
        <>
          <Typography variant="body1" paragraph>
            Your task is ready to be submitted. Click the button below to create your task.
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleSubmit}
              disabled={submitting}
              startIcon={submitting && <CircularProgress size={20} />}
            >
              {submitting ? 'Submitting...' : 'Submit Task'}
            </Button>
          </Box>
        </>
      ) : (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <CheckCircle color="success" sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Task Successfully Created!
          </Typography>
          <Typography variant="body1" paragraph>
            Your task has been successfully created and saved.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGoToTasks}
            sx={{ mt: 2 }}
          >
            Go to Task Dashboard
          </Button>
        </Box>
      )}
    </TaskStepper>
  );
};

export default TaskSubmitPage;