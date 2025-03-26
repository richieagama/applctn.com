// src/pages/task/TaskSetupPage.js
import React, { useState } from 'react';
import { Typography, Grid, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';
import TaskStepper from '../../components/TaskStepper';

const TaskSetupPage = () => {
  const [setupData, setSetupData] = useState({
    priority: 'medium',
    dueDate: '',
    assignee: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSetupData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <TaskStepper>
      <Typography variant="h5" gutterBottom>
        Task Setup
      </Typography>
      <Typography variant="body1" paragraph>
        Configure the basic parameters for your task.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Priority</InputLabel>
            <Select
              name="priority"
              value={setupData.priority}
              onChange={handleChange}
              label="Priority"
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Due Date"
            name="dueDate"
            type="date"
            value={setupData.dueDate}
            onChange={handleChange}
            InputLabelProps={{
              shrink: true,
            }}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Assignee"
            name="assignee"
            value={setupData.assignee}
            onChange={handleChange}
            variant="outlined"
          />
        </Grid>
      </Grid>
    </TaskStepper>
  );
};

export default TaskSetupPage;