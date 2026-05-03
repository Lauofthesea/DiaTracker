import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Activity, History, Info } from 'lucide-react';
import ResponsiveLayout from '../ResponsiveLayout';
import Breadcrumb from '../Breadcrumb';
import HealthCheckForm from './HealthCheckForm';
import ConsentNotice from './ConsentNotice';
import ProcessingIndicator from './ProcessingIndicator';
import PredictionResultCard from './PredictionResultCard';
import { submitHealthCheck, getHealthCheckHistory, HealthCheckSubmitRequest, HealthCheckSubmitResponse } from '@/lib/healthCheck';
import { Prediction } from '@/lib/types';
import { handleApiError } from '@/lib/api';

type PageStep = 'form' | 'consent' | 'processing' | 'results';

export default function HealthCheckPage() {
  const [currentStep, setCurrentStep] = useState<PageStep>('form');
  const [formData, setFormData] = useState<HealthCheckSubmitRequest | null>(null);
  const [predictionResult, setPredictionResult] = useState<HealthCheckSubmitResponse | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [error, setError] = useState<string>('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const data = await getHealthCheckHistory();
      setHistory(data || []); // Ensure we always have an array
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistory([]); // Set empty array on error
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleFormSubmit = (data: HealthCheckSubmitRequest) => {
    setFormData(data);
    setCurrentStep('consent');
  };

  const handleConsentAccept = async () => {
    if (!formData) return;

    setCurrentStep('processing');
    setError('');

    try {
      // Start the health check submission
      const startTime = Date.now();
      const result = await submitHealthCheck(formData);
      
      // Calculate elapsed time
      const elapsedTime = Date.now() - startTime;
      const minimumDisplayTime = 2500; // 2.5 seconds minimum
      
      // If the request completed too quickly, wait for the remaining time
      if (elapsedTime < minimumDisplayTime) {
        await new Promise(resolve => setTimeout(resolve, minimumDisplayTime - elapsedTime));
      }
      
      setPredictionResult(result);
      setCurrentStep('results');
      // Reload history after new prediction
      await loadHistory();
    } catch (err) {
      setError(handleApiError(err));
      setCurrentStep('form');
    }
  };

  const handleConsentDecline = () => {
    setCurrentStep('form');
  };

  const handleResultsComplete = () => {
    setCurrentStep('form');
    setFormData(null);
    setPredictionResult(null);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getClassificationColor = (classification: string) => {
    if (classification === 'No Diabetes') return 'text-green-600 bg-green-50';
    if (classification === 'Type 1') return 'text-red-600 bg-red-50';
    return 'text-orange-600 bg-orange-50';
  };

  // Breadcrumb items based on current step
  const getBreadcrumbItems = () => {
    const items = [{ label: 'Health Check' }];
    if (currentStep === 'consent') {
      items.push({ label: 'Privacy & Consent' });
    } else if (currentStep === 'processing') {
      items.push({ label: 'Processing' });
    } else if (currentStep === 'results') {
      items.push({ label: 'Results' });
    }
    return items;
  };

  return (
    <ResponsiveLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {currentStep !== 'form' && <Breadcrumb items={getBreadcrumbItems()} />}
          
          <div className="mb-6">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Health Check</h1>
            <p className="text-gray-600 mt-1 text-sm sm:text-base">Assess your diabetes risk with our ML-powered prediction</p>
          </div>

          <Tabs defaultValue="assessment" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2 max-w-md">
              <TabsTrigger value="assessment" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                New Assessment
              </TabsTrigger>
              <TabsTrigger value="history" className="flex items-center gap-2">
                <History className="h-4 w-4" />
                History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="assessment" className="space-y-6">
              {currentStep === 'form' && (
                <Card className="max-w-3xl">
                  <CardHeader>
                    <CardTitle>Health Metrics</CardTitle>
                    <CardDescription>
                      Enter your current health information for diabetes risk assessment
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <HealthCheckForm onSubmit={handleFormSubmit} error={error} />
                  </CardContent>
                </Card>
              )}

              {currentStep === 'consent' && (
                <Card className="max-w-3xl">
                  <CardHeader>
                    <CardTitle>Privacy & Consent</CardTitle>
                    <CardDescription>
                      Review how we'll use your health information
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ConsentNotice
                      onAccept={handleConsentAccept}
                      onDecline={handleConsentDecline}
                    />
                  </CardContent>
                </Card>
              )}

              {currentStep === 'processing' && (
                <Card className="max-w-3xl">
                  <CardHeader>
                    <CardTitle>Analyzing Your Health Data</CardTitle>
                    <CardDescription>
                      Our ML model is processing your information...
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ProcessingIndicator />
                  </CardContent>
                </Card>
              )}

              {currentStep === 'results' && predictionResult && (
                <Card className="max-w-3xl">
                  <CardHeader>
                    <CardTitle>Your Diabetes Risk Assessment</CardTitle>
                    <CardDescription>
                      Based on the health metrics you provided
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <PredictionResultCard
                      prediction={predictionResult}
                      onComplete={handleResultsComplete}
                    />
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              {isLoadingHistory ? (
                <Card className="max-w-3xl">
                  <CardContent className="pt-6">
                    <div className="text-center text-gray-500">Loading history...</div>
                  </CardContent>
                </Card>
              ) : !history || history.length === 0 ? (
                <Card className="max-w-3xl">
                  <CardContent className="pt-6">
                    <div className="text-center py-8">
                      <History className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">No health check history yet</p>
                      <p className="text-sm text-gray-500 mt-1">
                        Complete your first assessment to see results here
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4 max-w-3xl">
                  {history.map((prediction) => (
                    <Card key={prediction.prediction_id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2 flex-wrap">
                              <span
                                className={`px-3 py-1 rounded-full text-sm font-semibold ${getClassificationColor(
                                  prediction.classification
                                )}`}
                              >
                                {prediction.classification}
                              </span>
                              <span className="text-sm text-gray-500">
                                Confidence: {Math.round(prediction.confidence * 100)}%
                              </span>
                            </div>
                            <div className="text-sm text-gray-600 space-y-1">
                              <p>
                                <strong>Date:</strong> {formatDate(prediction.predicted_at)}
                              </p>
                              {prediction.metrics && (
                                <>
                                  <p>
                                    <strong>Weight:</strong> {prediction.metrics.weight_kg} kg
                                  </p>
                                  <p>
                                    <strong>Blood Sugar:</strong> {prediction.metrics.blood_sugar_mgdl} mg/dL
                                  </p>
                                  <p>
                                    <strong>Age:</strong> {prediction.metrics.age} years
                                  </p>
                                  {prediction.metrics.bmi && (
                                    <p>
                                      <strong>BMI:</strong> {prediction.metrics.bmi.toFixed(1)}
                                    </p>
                                  )}
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>

          <Alert className="mt-6 max-w-3xl">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-sm">
              <strong>Remember:</strong> These predictions are for informational purposes only. Always consult with a healthcare professional for medical advice and diagnosis.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </ResponsiveLayout>
  );
}
