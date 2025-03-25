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

const KeywordProcessorApp = () => {
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
    const fetchKeywords = async () => {
      try {
        const response = await fetch('/get-keywords');
        if (response.ok) {
          const data = await response.json();
          if (data.keywords && Array.isArray(data.keywords)) {
            setNegativeKeywords(data.keywords);
          }
        }
      } catch (error) {
        console.error('Failed to fetch keywords:', error);
      }
    };
  
    fetchKeywords();
  }, []);

  // Handle file selection
  const handleFileSelect = (e) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter(file => file.type === 'text/csv');
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  // Remove a file from the list
  const removeFile = (indexToRemove) => {
    setFiles(files.filter((_, index) => index !== indexToRemove));
  };

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

  // Handle form submission
  const handleSubmit = async () => {
    if (files.length === 0) {
      setUploadStatus({ severity: 'error', message: 'Please select at least one CSV file' });
      return;
    }
  
    setIsUploading(true);
    setUploadStatus({ severity: 'info', message: 'Processing files...' });
  
    try {
      // First, update the negative keywords on the server
      const keywordsResponse = await fetch('/update-keywords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keywords: negativeKeywords }),
      });
  
      if (!keywordsResponse.ok) {
        const errorData = await keywordsResponse.json();
        throw new Error(errorData.error || 'Failed to update keywords');
      }
      
      // Get the updated keywords from the response
      const keywordsData = await keywordsResponse.json();
      if (keywordsData.keywords) {
        setNegativeKeywords(keywordsData.keywords);
      }
  
      // Then, process the files
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
  
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'combined_spreadsheet.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setUploadStatus({ severity: 'success', message: 'Files processed successfully!' });
        setFiles([]);
      } else {
        const errorData = await response.json();
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
    <Container maxWidth="lg" sx={{ my: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Keyword Processor
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Upload CSV files, manage negative keywords, and process your data
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Left Column - File Upload */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>Upload Files</Typography>
            
            {/* Upload area */}
            <Box 
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                mb: 3,
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'rgba(25, 118, 210, 0.04)'
                },
                ...(isDragging && {
                  borderColor: 'primary.main',
                  bgcolor: 'rgba(25, 118, 210, 0.08)'
                })
              }}
              onClick={() => fileInputRef.current.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                if (e.dataTransfer.files) {
                  const newFiles = Array.from(e.dataTransfer.files).filter(file => file.type === 'text/csv');
                  setFiles(prev => [...prev, ...newFiles]);
                }
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body1" gutterBottom>
                Drag and drop CSV files here
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click to browse
              </Typography>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileSelect} 
                multiple 
                accept=".csv" 
                style={{ display: 'none' }} 
              />
            </Box>
            
            {/* File list */}
            <Typography variant="subtitle2" gutterBottom>
              Selected Files ({files.length})
            </Typography>
            {files.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
                No files selected
              </Typography>
            ) : (
              <List sx={{ maxHeight: 240, overflow: 'auto' }}>
                {files.map((file, index) => (
                  <ListItem key={index} sx={{ bgcolor: 'background.default', mb: 1, borderRadius: 1 }}>
                    <DescriptionIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <ListItemText primary={file.name} />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" onClick={() => removeFile(index)} size="small">
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
            
            {/* Process button */}
            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                fullWidth
                disabled={isUploading || files.length === 0}
                onClick={handleSubmit}
                startIcon={isUploading ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {isUploading ? 'Processing...' : 'Process Files'}
              </Button>
            </Box>
            
            {/* Status message */}
            {uploadStatus && (
              <Alert severity={uploadStatus.severity} sx={{ mt: 2 }}>
                {uploadStatus.message}
              </Alert>
            )}
          </Paper>
        </Grid>
        
        {/* Right Column - Negative Keywords */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>Negative Keywords</Typography>
            
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
                Add Keywords
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
                Current Keywords ({negativeKeywords.length})
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
            </Paper>
          </Paper>
        </Grid>
      </Grid>
      
      <Box component="footer" sx={{ mt: 6, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          © 2025 ptnrshp - All Rights Reserved
        </Typography>
      </Box>
    </Container>
  );
};

export default KeywordProcessorApp;