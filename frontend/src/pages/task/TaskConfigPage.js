import React, { useState, useRef, useEffect } from 'react';
import {
  Container, Typography, Paper, Box, Button, TextField, Chip,
  List, ListItem, ListItemText, ListItemSecondaryAction,
  IconButton, Divider, Grid, Alert, CircularProgress
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';


import TaskStepper from '../../components/TaskStepper';
import { useTaskContext } from '../../context/TaskContext';

const TaskConfigPage = () => {
  // State for file uploads
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  
  // State for negative keywords
  const [negativeKeywords, setNegativeKeywords] = useState([]);
  const [keywordInput, setKeywordInput] = useState('');
  const fileInputRef = useRef(null);

  // Fetch keywords from the server on component mount
  useEffect(() => {
    const fetchAsins = async () => {
      try {
        const response = await fetch('/get-asins');
        if (response.ok) {
          const data = await response.json();
          if (data.asins && Array.isArray(data.asins)) {
            setNegativeKeywords(data.asins);
          }
        }
      } catch (error) {
        console.error('Failed to fetch asins:', error);
      }
    };
  
    fetchAsins();
  }, []);




  // Handle negative keywords
  const handleKeywordInputChange = (e) => {
    setKeywordInput(e.target.value);
  };

  const addKeyword = () => {
    if (keywordInput.trim() === '') return;
    
    // Split input by newlines and process each keyword
    const keywordsToAdd = keywordInput
      .split(/\n/)
      .map(k => k.trim())
      .filter(k => k !== '' && !negativeKeywords.includes(k));
    
    if (keywordsToAdd.length > 0) {
      setNegativeKeywords([...negativeKeywords, ...keywordsToAdd]);
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword) => {
    setNegativeKeywords(negativeKeywords.filter(k => k !== keyword));
  };
  
  const clearAllKeywords = () => {
    setNegativeKeywords([]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      addKeyword();
    }
  };

  //get the files
  const handleDownload = async () => {
        // Create a download link
        const downloadLink = document.createElement('a');
        downloadLink.href = '/download-exports';
        downloadLink.download = 'exports.zip'; // This name is overridden by the server
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

  };

  // Handle form submission
  const handleSubmit = async () => {

  
    setIsUploading(true);
    setUploadStatus({ severity: 'info', message: 'Processing files...' });
  
    try {
      // First, send asins to server
      const botResponse = await fetch('/start-cerebro-bot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ asins: negativeKeywords }),
      });
  
      if (!botResponse.ok) {
        const errorData = await botResponse.json();
        throw new Error(errorData.error || 'Failed to update asins');
      }
      
      // Get the updated keywords from the response
      const asinData = await botResponse.json();
      if (asinData.asins) {
        setNegativeKeywords(asinData.asins);
      }
  

      if (botResponse.ok) {

        //send files here??
   
      } else {
        const errorData = await botResponse.json();
        setUploadStatus({ severity: 'error', message: errorData.error || 'Failed to process files' });
      }
    } catch (error) {
      setUploadStatus({ severity: 'error', message: 'An error occurred: ' + error.message });
      console.error('Error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
   <TaskStepper>
    <Container maxWidth="lg" sx={{ my: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Cerebro Bot
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Get Cerebro Reports in Bulk
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Left Column - File Upload */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>Cerebro Files</Typography>
            

            
            {/* csv file list area */}

            

          </Paper>
        </Grid>
        
        {/* Right Column - Negative Keywords */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>Enter ASINS</Typography>
            
            {/* Add keyword input */}
            <TextField
              multiline
              rows={3}
              fullWidth
              variant="outlined"
              placeholder="Add negative keywords (one per line for bulk input)..."
              value={keywordInput}
              onChange={handleKeywordInputChange}
              onKeyPress={handleKeyPress}
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                disabled={keywordInput.trim() === ''}
                onClick={addKeyword}
                sx={{ flexGrow: 1 }}
              >
                Add Asins
              </Button>
              <Button
                variant="outlined"
                onClick={clearAllKeywords}
              >
                Clear All
              </Button>
            </Box>
            
            {/* Keywords list */}
            <Paper variant="outlined" sx={{ p: 2, maxHeight: 320, overflow: 'auto' }}>
              <Typography variant="subtitle2" gutterBottom>
                Current ASINS ({negativeKeywords.length})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {negativeKeywords.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    onDelete={() => removeKeyword(keyword)}
                    sx={{ mb: 1 }}
                  />
                ))}
              </Box>

                          {/* Process button */}
                          <Box sx={{ mt: 3 }}>
                            <Button
                              variant="contained"
                              fullWidth
                              onClick={handleSubmit}
                              startIcon={isUploading ? <CircularProgress size={20} color="inherit" /> : null}
                            >
                              {isUploading ? 'Processing...' : 'Get Cerebro Reports'}
                            </Button>
                          </Box>


                          {/* Process button */}
                          <Box sx={{ mt: 3 }}>
                            <Button
                              variant="contained"
                              fullWidth
                              onClick={handleDownload}
                            >
                              {isUploading ? 'Processing...' : 'Download CSV Files'}
                            </Button>
                          </Box>                          

              
            </Paper>
          </Paper>
        </Grid>
      </Grid>
      
      <Box component="footer" sx={{ mt: 6, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          © 2025 Nuwatt - All Rights Reserved
        </Typography>
      </Box>
    </Container>


   </TaskStepper>
  );
};

export default TaskConfigPage;