import { useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Card, CardContent } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Progress } from '@/app/components/ui/progress';
import { CheckCircle2, AlertTriangle, Info, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import { HealthCheckSubmitResponse } from '@/lib/healthCheck';

interface PredictionResultCardProps {
  prediction: HealthCheckSubmitResponse;
  onComplete: () => void;
  healthMetrics?: {
    weight_kg: number;
    blood_sugar_mgdl: number;
    age: number;
    height_cm: number;
    bmi: number;
  };
  profileData?: {
    gender: string | null;
    family_history: boolean | null;
  };
}

export default function PredictionResultCard({ prediction, onComplete, healthMetrics, profileData }: PredictionResultCardProps) {
  const { classification, confidence } = prediction;
  const confidencePercentage = Math.round(confidence * 100);
  const [isExpanded, setIsExpanded] = useState(false);

  const getResultConfig = () => {
    // Use the classification directly from RF #2 model (Low, Mid, High)
    if (classification === 'High') {
      return {
        icon: AlertTriangle,
        iconColor: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        title: 'High Risk',
        message: 'Your health metrics suggest a high risk for diabetes.',
        recommendations: [
          'Consult with your healthcare provider immediately for proper diagnosis',
          'Monitor blood sugar levels closely - test before and after meals',
          'Reduce intake of high-sugar foods and refined carbohydrates',
          'Increase physical activity - aim for at least 150 minutes per week',
          'Consider working with a dietitian for a personalized meal plan',
          'Track your meals and blood sugar using our app to identify patterns',
        ],
      };
    }
    
    if (classification === 'Mid') {
      return {
        icon: AlertTriangle,
        iconColor: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        title: 'Mid Risk',
        message: 'Your health metrics show some concerning factors. Regular monitoring is recommended.',
        recommendations: [
          'Schedule a check-up with your healthcare provider',
          'Monitor your blood sugar levels regularly',
          'Focus on maintaining a healthy diet with balanced nutrition',
          'Increase physical activity - aim for 30 minutes daily',
          'Track your meals and carbohydrate intake',
          'Work towards achieving a healthy BMI if overweight',
        ],
      };
    }
    
    // Low risk
    return {
      icon: CheckCircle2,
      iconColor: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      title: 'Low Risk',
      message: 'Based on your health metrics, you show a low risk for diabetes.',
      recommendations: [
        'Maintain a healthy diet with balanced nutrition',
        'Stay physically active with regular exercise',
        'Monitor your blood sugar levels periodically',
        'Schedule regular check-ups with your healthcare provider',
      ],
    };
  };

  const getDetailedExplanation = () => {
    if (!healthMetrics) return null;

    const { blood_sugar_mgdl, bmi, age } = healthMetrics;
    const explanations: string[] = [];

    // Blood sugar analysis
    if (blood_sugar_mgdl >= 250) {
      explanations.push(`Your blood sugar level of ${blood_sugar_mgdl} mg/dL is significantly elevated. Normal fasting blood sugar is below 100 mg/dL, and levels above 200 mg/dL indicate diabetes. This is a major risk factor.`);
    } else if (blood_sugar_mgdl >= 180) {
      explanations.push(`Your blood sugar level of ${blood_sugar_mgdl} mg/dL is elevated. Normal fasting blood sugar is below 100 mg/dL. Levels between 100-125 mg/dL indicate prediabetes, and above 126 mg/dL suggests diabetes.`);
    } else if (blood_sugar_mgdl >= 126) {
      explanations.push(`Your blood sugar level of ${blood_sugar_mgdl} mg/dL is in the diabetic range. Normal fasting blood sugar is below 100 mg/dL.`);
    } else if (blood_sugar_mgdl >= 100) {
      explanations.push(`Your blood sugar level of ${blood_sugar_mgdl} mg/dL is in the prediabetic range. Normal fasting blood sugar is below 100 mg/dL.`);
    } else {
      explanations.push(`Your blood sugar level of ${blood_sugar_mgdl} mg/dL is within the normal range (below 100 mg/dL).`);
    }

    // BMI analysis
    if (bmi >= 30) {
      explanations.push(`Your BMI of ${bmi.toFixed(1)} indicates obesity (BMI ≥ 30). Obesity significantly increases diabetes risk as excess body fat can lead to insulin resistance.`);
    } else if (bmi >= 25) {
      explanations.push(`Your BMI of ${bmi.toFixed(1)} indicates you are overweight (BMI 25-29.9). Being overweight increases your risk of developing diabetes.`);
    } else if (bmi >= 18.5) {
      explanations.push(`Your BMI of ${bmi.toFixed(1)} is in the healthy range (18.5-24.9).`);
    } else {
      explanations.push(`Your BMI of ${bmi.toFixed(1)} indicates you are underweight (BMI < 18.5).`);
    }

    // Age analysis
    if (age >= 45) {
      explanations.push(`At age ${age}, your risk for diabetes increases. Age is a significant risk factor, especially after 45.`);
    } else if (age >= 35) {
      explanations.push(`At age ${age}, you should begin monitoring for diabetes risk factors.`);
    }

    // Family history analysis
    if (profileData?.family_history) {
      explanations.push(`You have a family history of diabetes, which increases your risk. Having a parent or sibling with diabetes significantly raises your likelihood of developing the condition.`);
    }

    return explanations;
  };

  const config = getResultConfig();
  const Icon = config.icon;
  const isLowConfidence = confidencePercentage < 70;
  const detailedExplanations = getDetailedExplanation();

  return (
    <div className="space-y-4 py-4">
      <Card className={`${config.bgColor} ${config.borderColor} border-2`}>
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-full ${config.bgColor}`}>
              <Icon className={`h-8 w-8 ${config.iconColor}`} />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-1">{config.title}</h3>
              <p className="text-sm text-gray-700">{config.message}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Confidence Score</span>
              <span className="text-lg font-bold text-primary">{confidencePercentage}%</span>
            </div>
            <Progress value={confidencePercentage} className="h-3" />
            <p className="text-xs text-gray-500">
              This score indicates how confident our ML model is in this prediction based on your health metrics.
            </p>
          </div>
        </CardContent>
      </Card>

      {isLowConfidence && (
        <Alert variant="default" className="bg-amber-50 border-amber-200">
          <Info className="h-4 w-4 text-amber-600" />
          <AlertDescription className="text-amber-900 text-sm">
            <strong>Note:</strong> The confidence score is below 70%. We strongly recommend consulting with a healthcare professional for a comprehensive evaluation.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardContent className="pt-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-gray-900">Recommended Actions</h4>
            </div>
            <ul className="space-y-2">
              {config.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-primary mt-0.5">•</span>
                  <span>{recommendation}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {healthMetrics && (
        <Card>
          <CardContent className="pt-4">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-between text-left"
            >
              <h4 className="font-semibold text-gray-900">Detailed Analysis</h4>
              {isExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>

            {isExpanded && (
              <div className="mt-4 space-y-4">
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Weight</p>
                    <p className="text-sm font-semibold text-gray-900">{healthMetrics.weight_kg} kg</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Blood Sugar</p>
                    <p className="text-sm font-semibold text-gray-900">{healthMetrics.blood_sugar_mgdl} mg/dL</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Age</p>
                    <p className="text-sm font-semibold text-gray-900">{healthMetrics.age} years</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">Height</p>
                    <p className="text-sm font-semibold text-gray-900">{healthMetrics.height_cm} cm</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 mb-1">BMI</p>
                    <p className="text-sm font-semibold text-gray-900">{healthMetrics.bmi.toFixed(1)}</p>
                  </div>
                  {profileData?.gender && (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Gender</p>
                      <p className="text-sm font-semibold text-gray-900">{profileData.gender}</p>
                    </div>
                  )}
                  {profileData?.family_history !== null && profileData?.family_history !== undefined && (
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Family History</p>
                      <p className="text-sm font-semibold text-gray-900">
                        {profileData.family_history ? 'Yes' : 'No'}
                      </p>
                    </div>
                  )}
                </div>

                {detailedExplanations && detailedExplanations.length > 0 && (
                  <div className="space-y-3">
                    <h5 className="font-semibold text-gray-900 text-sm">Why did I get this result?</h5>
                    <div className="space-y-2">
                      {detailedExplanations.map((explanation, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-gray-700">{explanation}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Alert variant="default" className="bg-blue-50 border-blue-200">
        <Info className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-900 text-sm">
          <strong>Medical Disclaimer:</strong> This prediction is generated by a machine learning model and is for informational purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
        </AlertDescription>
      </Alert>

      <Button onClick={onComplete} className="w-full" size="lg">
        Return to Dashboard
      </Button>
    </div>
  );
}
