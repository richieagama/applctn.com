// src/pages/task/TaskReviewPage.js
import React from 'react';
import { Typography, Grid, Paper, Box } from '@mui/material';
import TaskStepper from '../../components/TaskStepper';

// In a real application, you would get this data from context or state management
const taskData = {
  title: "Sample Task",
  description: "This is a sample task description",
  priority: "Medium",
  dueDate: "2025-04-15",
  assignee: "John Doe",
  notifications: true,
  reminders: true,
  tags: ["work", "important"]
};

const TaskReviewPage = () => {
  return (
    <TaskStepper>
      <Typography variant="h5" gutterBottom>
        Review Task
      </Typography>
      <Typography variant="body1" paragraph>
        Please review your task details before submitting.
      </Typography>
      
      <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Title</Typography>
            <Typography variant="body1" gutterBottom>{taskData.title}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Priority</Typography>
            <Typography variant="body1" gutterBottom>{taskData.priority}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Due Date</Typography>
            <Typography variant="body1" gutterBottom>{taskData.dueDate}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2">Assignee</Typography>
            <Typography variant="body1" gutterBottom>{taskData.assignee}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Description</Typography>
            <Typography variant="body1" paragraph>{taskData.description}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Settings</Typography>
            <Typography variant="body1">
              Notifications: {taskData.notifications ? 'Enabled' : 'Disabled'}
            </Typography>
            <Typography variant="body1">
              Reminders: {taskData.reminders ? 'Enabled' : 'Disabled'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="subtitle2">Tags</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {taskData.tags.map(tag => (
                <Box 
                  key={tag} 
                  sx={{ 
                    bgcolor: 'primary.light', 
                    color: 'white', 
                    px: 1, 
                    py: 0.5, 
                    borderRadius: 1,
                    fontSize: '0.875rem'
                  }}
                >
                  {tag}
                </Box>
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </TaskStepper>
  );
};

export default TaskReviewPage;