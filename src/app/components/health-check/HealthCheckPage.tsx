import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Activity, History } from 'lucide-react';
import ResponsiveLayout from '../ResponsiveLayout';
import Breadcrumb from '../Breadcrumb';
import HealthCheckForm from './HealthCheckForm';
import ConsentNotice from './ConsentNotice';
import ProcessingIndicator from './ProcessingIndicator';
import PredictionResultCard from './PredictionResultCard';
import { submitHealthCheck, getHealthCheckHistory, HealthCheckSubmitRequest, HealthCheckSubmitResponse } from '@/lib/healthCheck';
import { getProfile } from '@/lib/profileApi';
import { getDailySummary } from '@/lib/foodApi';
import { Prediction } from '@/lib/types';
import { handleApiError } from '@/lib/api';
import type { ProfileResponse } from '@/types/profile';

type PageStep = 'form' | 'consent' | 'processing' | 'results';

export default function HealthCheckPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<PageStep>('form');
  const [formData, setFormData] = useState<HealthCheckSubmitRequest | null>(null);
  const [predictionResult, setPredictionResult] = useState<HealthCheckSubmitResponse | null>(null);
  const [history, setHistory] = useState<Prediction[]>([]);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [error, setError] = useState<string>('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [hasMealsInLast24Hours, setHasMealsInLast24Hours] = useState(false);

  useEffect(() => {
    loadHistory();
    loadProfile();
    checkRecentMeals();
  }, []);

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

  const loadProfile = async () => {
    try {
      const profileData = await getProfile();
      setProfile(profileData);
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const data = await getHealthCheckHistory();
      setHistory(data || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistory([]);
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
      const startTime = Date.now();
      const result = await submitHealthCheck(formData);
      
      const elapsedTime = Date.now() - startTime;
      const minimumDisplayTime = hasMealsInLast24Hours ? 28000 : 24000;
      
      if (elapsedTime < minimumDisplayTime) {
        await new Promise(resolve => setTimeout(resolve, minimumDisplayTime - elapsedTime));
      }
      
      setPredictionResult(result);
      setCurrentStep('results');
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
    navigate('/');
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

  const getRiskLevel = (classification: string, confidence: number, probabilities?: Record<string, number>) => {
    if (classification === 'Has Diabetes') {
      return { level: 'High Risk', color: 'text-red-600 bg-red-50' };
    }
    
    // For "No Diabetes" - check confidence and probability
    const diabetesProbability = probabilities?.['Has Diabetes'] || 0;
    const isHighProbability = diabetesProbability >= 0.3;
    const isLowConfidence = confidence < 0.75;
    
    if (isHighProbability || isLowConfidence) {
      return { level: 'Medium Risk', color: 'text-orange-600 bg-orange-50' };
    }
    
    return { level: 'Low Risk', color: 'text-green-600 bg-green-50' };
  };

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
                    <HealthCheckForm 
                      onSubmit={handleFormSubmit} 
                      error={error}
                      profileData={{
                        age: profile?.age || null,
                        height_cm: profile?.height_cm || null
                      }}
                      lastHealthCheck={
                        history.length > 0
                          ? {
                              weight_kg: history[0].health_metrics.weight_kg,
                              blood_sugar_mgdl: history[0].health_metrics.blood_sugar_mgdl,
                            }
                          : null
                      }
                    />
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
                    <ProcessingIndicator hasMealsInLast24Hours={hasMealsInLast24Hours} />
                  </CardContent>
                </Card>
              )}

              {currentStep === 'results' && predictionResult && formData && (
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
                      healthMetrics={{
                        weight_kg: formData.weight_unit === 'lbs' ? formData.weight * 0.453592 : formData.weight,
                        blood_sugar_mgdl: formData.blood_sugar,
                        age: formData.age,
                        height_cm: formData.height_unit === 'in' ? formData.height * 2.54 : formData.height,
                        bmi: (() => {
                          const weightKg = formData.weight_unit === 'lbs' ? formData.weight * 0.453592 : formData.weight;
                          const heightCm = formData.height_unit === 'in' ? formData.height * 2.54 : formData.height;
                          const heightM = heightCm / 100;
                          return weightKg / (heightM * heightM);
                        })(),
                        symptoms: formData.symptoms,
                      }}
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
                  {history.map((prediction) => {
                    const riskInfo = getRiskLevel(prediction.classification, prediction.confidence, prediction.probabilities);
                    return (
                    <Card key={prediction.prediction_id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3 flex-wrap">
                              <span
                                className={`px-3 py-1.5 rounded-full text-sm font-semibold ${riskInfo.color}`}
                              >
                                {riskInfo.level}
                              </span>
                              <span className="text-sm font-medium text-gray-700">
                                Confidence: {Math.round(prediction.confidence * 100)}%
                              </span>
                            </div>
                            <div className="text-sm text-gray-600">
                              <p className="mb-2">
                                <strong>Date:</strong> {formatDate(prediction.predicted_at)}
                              </p>
                            </div>
                          </div>
                        </div>
                        
                        {prediction.health_metrics && (
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 bg-gray-50 rounded-lg">
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Weight</p>
                              <p className="text-sm font-semibold text-gray-900">{prediction.health_metrics.weight_kg} kg</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Blood Sugar</p>
                              <p className="text-sm font-semibold text-gray-900">{prediction.health_metrics.blood_sugar_mgdl} mg/dL</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Age</p>
                              <p className="text-sm font-semibold text-gray-900">{prediction.health_metrics.age} years</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Height</p>
                              <p className="text-sm font-semibold text-gray-900">{prediction.health_metrics.height_cm} cm</p>
                            </div>
                            {prediction.health_metrics.bmi && (
                              <div>
                                <p className="text-xs text-gray-500 mb-1">BMI</p>
                                <p className="text-sm font-semibold text-gray-900">{prediction.health_metrics.bmi.toFixed(1)}</p>
                              </div>
                            )}
                            {prediction.health_metrics.symptoms && prediction.health_metrics.symptoms.length > 0 && (
                              <div className="col-span-2 sm:col-span-3">
                                <p className="text-xs text-gray-500 mb-1">Symptoms</p>
                                <p className="text-sm text-gray-700">{prediction.health_metrics.symptoms.join(', ')}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                  })}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </ResponsiveLayout>
  );
}
