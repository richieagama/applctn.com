import React from 'react';
import { TextField, Typography, Grid } from '@mui/material';
import TaskStepper from '../../components/TaskStepper';
import { useTaskContext } from '../../context/TaskContext';

const TaskDetailsPage = () => {
  const { taskData, updateTaskData } = useTaskContext();

  const handleChange = (e) => {
    const { name, value } = e.target;
    updateTaskData({ [name]: value });
  };

  return (
    <TaskStepper>
      <Typography variant="h5" gutterBottom>
        Task Details
      </Typography>
      <Typography variant="body1" paragraph>
        Enter the basic information about your task.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Task Title"
            name="title"
            value={taskData.title}
            onChange={handleChange}
            variant="outlined"
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Task Description"
            name="description"
            value={taskData.description}
            onChange={handleChange}
            variant="outlined"
            multiline
            rows={4}
          />
        </Grid>
      </Grid>
    </TaskStepper>
  );
};

export default TaskDetailsPage;