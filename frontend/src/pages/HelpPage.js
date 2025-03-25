import React from 'react';
import { Container, Typography, Paper, Box, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const HelpPage = () => {
  return (
    <Container maxWidth="lg" sx={{ my: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Help & FAQ
        </Typography>
        
        <Box sx={{ mt: 3 }}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">What file formats are supported?</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Currently, the application supports CSV files only. The files must contain a column named "Keyword Phrase".
              </Typography>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">How do negative keywords work?</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Negative keywords are used to filter out rows from your CSV files. If a row's "Keyword Phrase" contains any of your specified negative keywords, it will be excluded from the final output.
              </Typography>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Can I process multiple files at once?</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                Yes! You can upload and process multiple CSV files simultaneously. The application will combine all the filtered data into a single Excel spreadsheet.
              </Typography>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">Where are my processed files saved?</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography>
                The processed Excel file will be automatically downloaded to your browser's default download location.
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      </Paper>
    </Container>
  );
};

export default HelpPage;