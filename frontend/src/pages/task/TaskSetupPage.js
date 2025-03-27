// src/pages/task/TaskSetupPage.js
import React, { useState, useEffect } from 'react';
import {
  Typography,
  Grid,
  TextField,
  Button,
  Box,
  Paper,
} from '@mui/material';
import TaskStepper from '../../components/TaskStepper';

  const TaskSetupPage = () => {
    const [mainText, setMainText] = useState('');
    const [keywordInput, setKeywordInput] = useState('');
    const [resultText, setResultText] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
  
    const findBracketedWords = (text) => {
      const regex = /\[(.*?)\]/g;
      return text.match(regex) || [];
    };
  
    const extractKeywords = (text) =>
      text.split('\n').filter((keyword) => keyword.trim() !== '');
  
    const cleanText = (text) =>
      text.replace(/\n\s*\n\s*\n/g, '\n\n').trim();
  
    const bracketedWords = findBracketedWords(mainText);
    const keywords = extractKeywords(keywordInput);
  
    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text);
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    };
  
    const handleSubmit = () => {
      if (keywords.length < bracketedWords.length) {
        setErrorMessage('Not enough keywords for the provided text.');
        return;
      }
  
      let updatedText = mainText;
      bracketedWords.forEach((word, index) => {
        updatedText = updatedText.replace(word, `[${keywords[index]}]`);
      });
  
      setResultText(updatedText);
      setErrorMessage('');
    };
  
    return (
    <TaskStepper>
      <Box sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Keyword Replacement Tool
        </Typography>
  
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>Text Entry</Typography>
          <Typography variant="body2" gutterBottom>
            Number of text enclosed in brackets: {bracketedWords.length}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={6}
            value={mainText}
            onChange={(e) => setMainText(cleanText(e.target.value))}
            placeholder="Enter your text with [bracketed keywords]"
            sx={{ mb: 2 }}
          />
  
          <Typography variant="subtitle1">Keywords Found:</Typography>
          <Box sx={{ mb: 2 }}>
            {bracketedWords.map((word, idx) => (
              <span key={idx}>
                {word.replace(/[\[\]]/g, '')}
                {idx < bracketedWords.length - 1 && ', '}
              </span>
            ))}
          </Box>
  
          <Grid container spacing={2}>
            <Grid item>
              <Button
                variant="contained"
                disabled={bracketedWords.length === 0}
                onClick={() =>
                  copyToClipboard(
                    bracketedWords
                      .map((word) => word.replace(/[\[\]]/g, ''))
                      .join('\n')
                  )
                }
              >
                Copy Keywords in Brackets
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                disabled={bracketedWords.length === 0}
                onClick={() =>
                  copyToClipboard(mainText.replace(/\[(.*?)\]/g, '$1'))
                }
              >
                Copy Text Without Brackets
              </Button>
            </Grid>
          </Grid>
        </Paper>
  
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>Replacement Keywords</Typography>
          <Typography variant="body2" gutterBottom>
            Number of keywords: {keywords.length}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            placeholder="Enter replacement keywords (one per line)"
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handleSubmit}>
            Submit
          </Button>
          {errorMessage && (
            <Typography color="error" sx={{ mt: 2 }}>
              {errorMessage}
            </Typography>
          )}
        </Paper>
  
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>Result</Typography>
          <TextField
            fullWidth
            multiline
            rows={6}
            value={resultText}
            InputProps={{ readOnly: true }}
            placeholder="Processed text will appear here"
            sx={{ mb: 2 }}
          />
          <Grid container spacing={2}>
            <Grid item>
              <Button
                variant="contained"
                disabled={resultText.trim() === ''}
                onClick={() =>
                  copyToClipboard(resultText.replace(/\[(.*?)\]/g, '$1'))
                }
              >
                Copy Processed Text Without Brackets
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="contained"
                disabled={resultText.trim() === ''}
                onClick={() => copyToClipboard(resultText)}
              >
                Copy Processed Text With Brackets
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Box>


      
    </TaskStepper>
    );
  };

export default TaskSetupPage;