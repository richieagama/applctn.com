// src/components/TaskStepper.js
import React, { useState, useEffect } from 'react';
import { 
  Stepper, 
  Step, 
  StepLabel, 
  Button, 
  Typography, 
  Box, 
  Paper,
  Container
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';

const steps = ['Task Details', 'Setup', 'Configuration', 'Review', 'Submit'];
const stepPaths = ['/task/details', '/task/setup', '/task/config', '/task/review', '/task/submit'];

const TaskStepper = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeStep, setActiveStep] = useState(0);

  // Determine active step based on current route
  useEffect(() => {
    const currentPath = location.pathname;
    const stepIndex = stepPaths.findIndex(path => path === currentPath);
    if (stepIndex !== -1) {
      setActiveStep(stepIndex);
    }
  }, [location.pathname]);

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
      navigate(stepPaths[activeStep + 1]);
    }
  };

  const handleBack = () => {
    if (activeStep > 0) {
      navigate(stepPaths[activeStep - 1]);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <div>
          <Box sx={{ mb: 2 }}>
            {children}
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', pt: 2 }}>
            <Button
              variant="contained"
              color="inherit"
              disabled={activeStep === 0}
              onClick={handleBack}
            >
              Back
            </Button>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleNext}
              disabled={activeStep === steps.length - 1}
            >
              {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
            </Button>
          </Box>
        </div>
      </Paper>
    </Container>
  );
};

export default TaskStepper;