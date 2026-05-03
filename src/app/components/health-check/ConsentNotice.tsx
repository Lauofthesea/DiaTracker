import { Button } from '@/app/components/ui/button';
import { Card, CardContent } from '@/app/components/ui/card';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Shield, Lock, Database, Eye, AlertCircle } from 'lucide-react';

interface ConsentNoticeProps {
  onAccept: () => void;
  onDecline: () => void;
}

export default function ConsentNotice({ onAccept, onDecline }: ConsentNoticeProps) {
  return (
    <div className="space-y-4 py-4">
      <Alert className="bg-blue-50 border-blue-200">
        <Shield className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-900">
          Your privacy and data security are our top priorities. Please review how we handle your health information.
        </AlertDescription>
      </Alert>

      <div className="space-y-3">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Database className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-sm mb-1">Data Storage</h3>
                <p className="text-sm text-gray-600">
                  Your health metrics will be securely stored in our encrypted database. We use AES-256 encryption to protect your data at rest.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Lock className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-sm mb-1">Data Usage</h3>
                <p className="text-sm text-gray-600">
                  Your information will be used exclusively for diabetes risk prediction and personalized health insights. We will never sell or share your data with third parties.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <Eye className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-sm mb-1">Confidentiality</h3>
                <p className="text-sm text-gray-600">
                  Your health data is kept strictly confidential within the system. Only you can access your personal health information and predictions.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-sm mb-1">ML Model Processing</h3>
                <p className="text-sm text-gray-600">
                  Your data will be processed by our machine learning model to generate a diabetes risk prediction. The model analyzes patterns in your health metrics to provide personalized insights.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Alert variant="default" className="bg-amber-50 border-amber-200">
        <AlertCircle className="h-4 w-4 text-amber-600" />
        <AlertDescription className="text-amber-900 text-sm">
          <strong>Important:</strong> This prediction is for informational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for medical decisions.
        </AlertDescription>
      </Alert>

      <div className="flex gap-3 pt-2">
        <Button
          type="button"
          variant="outline"
          onClick={onDecline}
          className="flex-1"
        >
          Go Back
        </Button>
        <Button
          type="button"
          onClick={onAccept}
          className="flex-1"
        >
          I Understand & Agree
        </Button>
      </div>
    </div>
  );
}
