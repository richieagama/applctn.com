import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const AboutPage = () => {
  return (
    <Container maxWidth="lg" sx={{ my: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          About Keyword Processor
        </Typography>
        <Typography paragraph>
          Keyword Processor is a tool designed to help filter and process CSV files based on keywords.
        </Typography>
        <Typography paragraph>
          The application allows you to upload CSV files containing keyword phrases, filter out unwanted keywords,
          and combine the results into a single Excel spreadsheet.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            How It Works
          </Typography>
          <Typography paragraph>
            1. Upload your CSV files containing a "Keyword Phrase" column
          </Typography>
          <Typography paragraph>
            2. Manage your list of negative keywords
          </Typography>
          <Typography paragraph>
            3. Process the files to filter out rows containing your negative keywords
          </Typography>
          <Typography paragraph>
            4. Download the combined results as an Excel file
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default AboutPage;