// src/pages/task/TaskConfigPage.js
import React, { useState } from 'react';
import { Typography, Grid, Checkbox, FormControlLabel, TextField, Chip, Box } from '@mui/material';
import TaskStepper from '../../components/TaskStepper';

const TaskConfigPage = () => {
  const [configData, setConfigData] = useState({
    notifications: true,
    reminders: true,
    tags: ['work'],
    tagInput: ''
  });

  const handleChange = (e) => {
    const { name, checked, value, type } = e.target;
    setConfigData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleTagInputChange = (e) => {
    setConfigData(prev => ({
      ...prev,
      tagInput: e.target.value
    }));
  };

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && configData.tagInput.trim() !== '') {
      setConfigData(prev => ({
        ...prev,
        tags: [...prev.tags, prev.tagInput.trim()],
        tagInput: ''
      }));
      e.preventDefault();
    }
  };

  const handleDeleteTag = (tagToDelete) => {
    setConfigData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToDelete)
    }));
  };

  return (
    <TaskStepper>
      <Typography variant="h5" gutterBottom>
        Task Configuration
      </Typography>
      <Typography variant="body1" paragraph>
        Configure additional settings for your task.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={configData.notifications}
                onChange={handleChange}
                name="notifications"
                color="primary"
              />
            }
            label="Enable notifications"
          />
        </Grid>
        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Checkbox
                checked={configData.reminders}
                onChange={handleChange}
                name="reminders"
                color="primary"
              />
            }
            label="Send reminders"
          />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Tags
          </Typography>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Add tags and press Enter"
            value={configData.tagInput}
            onChange={handleTagInputChange}
            onKeyDown={handleAddTag}
            size="small"
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {configData.tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onDelete={() => handleDeleteTag(tag)}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        </Grid>
      </Grid>
    </TaskStepper>
  );
};

export default TaskConfigPage;