import { Button } from '@/app/components/ui/button';
import { Card, CardContent } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Progress } from '@/app/components/ui/progress';
import { CheckCircle2, AlertTriangle, Info, TrendingUp } from 'lucide-react';
import { HealthCheckSubmitResponse } from '@/lib/healthCheck';

interface PredictionResultCardProps {
  prediction: HealthCheckSubmitResponse;
  onComplete: () => void;
}

export default function PredictionResultCard({ prediction, onComplete }: PredictionResultCardProps) {
  const { classification, confidence } = prediction;
  const confidencePercentage = Math.round(confidence * 100);

  const getResultConfig = () => {
    if (classification === 'Has Diabetes') {
      return {
        icon: AlertTriangle,
        iconColor: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        title: 'High Risk - Diabetes Detected',
        message: 'Your health metrics suggest a high risk for diabetes.',
        recommendations: [
          'Schedule an appointment with your healthcare provider immediately',
          'Monitor blood sugar levels closely and regularly',
          'Focus on dietary changes to manage blood sugar',
          'Increase physical activity and exercise regularly',
          'Track your carbohydrate intake using our meal logging feature',
        ],
      };
    }
    
    const diabetesProbability = prediction.probabilities?.['Has Diabetes'] || 0;
    const isHighProbability = diabetesProbability >= 0.3;
    const isLowConfidence = confidence < 0.75;
    
    if (isHighProbability || isLowConfidence) {
      return {
        icon: AlertTriangle,
        iconColor: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        title: 'Medium Risk - Monitor Closely',
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

  const config = getResultConfig();
  const Icon = config.icon;
  const isLowConfidence = confidencePercentage < 70;

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
