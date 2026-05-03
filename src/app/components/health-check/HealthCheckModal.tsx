import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/app/components/ui/dialog';
import HealthCheckForm from './HealthCheckForm';
import ConsentNotice from './ConsentNotice';
import ProcessingIndicator from './ProcessingIndicator';
import PredictionResultCard from './PredictionResultCard';
import { submitHealthCheck, HealthCheckSubmitRequest, HealthCheckSubmitResponse } from '@/lib/healthCheck';
import { handleApiError } from '@/lib/api';
import { getDailySummary } from '@/lib/foodApi';

interface HealthCheckModalProps {
  open: boolean;
  onComplete: () => void;
  profileData?: { age: number | null; height_cm: number | null };
}

type ModalStep = 'welcome' | 'form' | 'consent' | 'processing' | 'results';

export default function HealthCheckModal({ open, onComplete, profileData }: HealthCheckModalProps) {
  const [currentStep, setCurrentStep] = useState<ModalStep>('welcome');
  const [formData, setFormData] = useState<HealthCheckSubmitRequest | null>(null);
  const [predictionResult, setPredictionResult] = useState<HealthCheckSubmitResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [hasMealsInLast24Hours, setHasMealsInLast24Hours] = useState(false);

  // Check for meals in last 24 hours when modal opens
  useEffect(() => {
    if (open) {
      checkRecentMeals();
    }
  }, [open]);

  const checkRecentMeals = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const summary = await getDailySummary(today);
      setHasMealsInLast24Hours(summary.total_calories > 0);
    } catch (err) {
      console.error('Error checking recent meals:', err);
      setHasMealsInLast24Hours(false);
    }
  };

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setCurrentStep('welcome');
      setFormData(null);
      setPredictionResult(null);
      setError('');
    }
  }, [open]);

  const handleFormSubmit = (data: HealthCheckSubmitRequest) => {
    setFormData(data);
    setCurrentStep('consent');
  };

  const handleConsentAccept = async () => {
    if (!formData) return;

    setCurrentStep('processing');
    setError('');

    try {
      const startTime = Date.now();
      const result = await submitHealthCheck(formData);
      
      const elapsedTime = Date.now() - startTime;
      const minimumDisplayTime = hasMealsInLast24Hours ? 28000 : 24000;
      
      if (elapsedTime < minimumDisplayTime) {
        await new Promise(resolve => setTimeout(resolve, minimumDisplayTime - elapsedTime));
      }
      
      setPredictionResult(result);
      setCurrentStep('results');
    } catch (err) {
      setError(handleApiError(err));
      setCurrentStep('form');
    }
  };

  const handleConsentDecline = () => {
    setCurrentStep('form');
  };

  const handleResultsComplete = () => {
    onComplete();
  };

  const handleWelcomeContinue = () => {
    setCurrentStep('form');
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent 
        className="max-w-2xl max-h-[90vh] overflow-y-auto [&>button]:hidden"
        onInteractOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        {currentStep === 'welcome' && (
          <>
            <DialogHeader>
              <DialogTitle className="text-2xl">Welcome to ML Diabetes Tracker</DialogTitle>
              <DialogDescription className="text-base pt-2">
                Let's start by assessing your diabetes risk. This quick health check will help us provide personalized insights.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">What to expect:</h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>We'll collect basic health metrics (weight, blood sugar, age, height)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>You'll review how your data will be used</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Our ML model will analyze your risk for diabetes</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>You'll receive immediate results with confidence scores</span>
                  </li>
                </ul>
              </div>
              <button
                onClick={handleWelcomeContinue}
                className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary/90 transition-colors"
              >
                Get Started
              </button>
            </div>
          </>
        )}

        {currentStep === 'form' && (
          <>
            <DialogHeader>
              <DialogTitle>Health Assessment</DialogTitle>
              <DialogDescription>
                Please provide your current health metrics for diabetes risk assessment.
              </DialogDescription>
            </DialogHeader>
            <HealthCheckForm onSubmit={handleFormSubmit} error={error} profileData={profileData} />
          </>
        )}

        {currentStep === 'consent' && (
          <>
            <DialogHeader>
              <DialogTitle>Privacy & Consent</DialogTitle>
              <DialogDescription>
                Please review how we'll use your health information.
              </DialogDescription>
            </DialogHeader>
            <ConsentNotice
              onAccept={handleConsentAccept}
              onDecline={handleConsentDecline}
            />
          </>
        )}

        {currentStep === 'processing' && (
          <>
            <DialogHeader>
              <DialogTitle>Analyzing Your Health Data</DialogTitle>
              <DialogDescription>
                Our ML model is processing your information...
              </DialogDescription>
            </DialogHeader>
            <ProcessingIndicator hasMealsInLast24Hours={hasMealsInLast24Hours} />
          </>
        )}

        {currentStep === 'results' && predictionResult && (
          <>
            <DialogHeader>
              <DialogTitle>Your Diabetes Risk Assessment</DialogTitle>
              <DialogDescription>
                Based on the health metrics you provided.
              </DialogDescription>
            </DialogHeader>
            <PredictionResultCard
              prediction={predictionResult}
              onComplete={handleResultsComplete}
            />
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
