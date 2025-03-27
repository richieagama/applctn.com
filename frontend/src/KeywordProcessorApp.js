import React, { useState, useRef, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';

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
 

  return (
    <Container  sx={{ display: 'flex' }} style={{ width: '100%', padding: '1em'}}>


<Button  variant='contained' component={RouterLink} to="/task/details">Start Here</Button>


    </Container>





  );
};

export default KeywordProcessorApp;