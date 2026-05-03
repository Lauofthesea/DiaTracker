import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/app/components/ui/card';
import { Progress } from '@/app/components/ui/progress';
import { Loader2, CheckCircle2 } from 'lucide-react';

const PROCESSING_STEPS = [
  { id: 1, label: 'Validating health metrics', duration: 800 },
  { id: 2, label: 'Preprocessing data', duration: 1000 },
  { id: 3, label: 'Loading ML model', duration: 1200 },
  { id: 4, label: 'Analyzing patterns', duration: 1500 },
  { id: 5, label: 'Calculating confidence scores', duration: 1000 },
  { id: 6, label: 'Generating prediction', duration: 800 },
];

export default function ProcessingIndicator() {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let stepTimer: ReturnType<typeof setTimeout>;
    let progressTimer: ReturnType<typeof setInterval>;

    const startNextStep = (stepIndex: number) => {
      if (stepIndex >= PROCESSING_STEPS.length) {
        setProgress(100);
        return;
      }

      setCurrentStep(stepIndex);
      const step = PROCESSING_STEPS[stepIndex];
      const progressIncrement = 100 / PROCESSING_STEPS.length;
      const startProgress = stepIndex * progressIncrement;
      const endProgress = (stepIndex + 1) * progressIncrement;

      // Animate progress for this step
      let currentProgress = startProgress;
      const progressStep = (endProgress - startProgress) / (step.duration / 50);

      progressTimer = setInterval(() => {
        currentProgress += progressStep;
        if (currentProgress >= endProgress) {
          currentProgress = endProgress;
          clearInterval(progressTimer);
        }
        setProgress(Math.min(currentProgress, 100));
      }, 50);

      // Move to next step after duration
      stepTimer = setTimeout(() => {
        startNextStep(stepIndex + 1);
      }, step.duration);
    };

    startNextStep(0);

    return () => {
      clearTimeout(stepTimer);
      clearInterval(progressTimer);
    };
  }, []);

  return (
    <div className="space-y-6 py-8">
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="relative">
          <Loader2 className="h-16 w-16 text-primary animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-12 w-12 rounded-full bg-primary/10" />
          </div>
        </div>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900">
            Analyzing Your Health Data
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            This may take a few moments...
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <Progress value={progress} className="h-2" />
        <p className="text-xs text-center text-gray-500">
          {Math.round(progress)}% complete
        </p>
      </div>

      <Card className="bg-gray-50">
        <CardContent className="pt-4">
          <div className="space-y-3">
            {PROCESSING_STEPS.map((step, index) => {
              const isCompleted = index < currentStep;
              const isCurrent = index === currentStep;
              const isPending = index > currentStep;

              return (
                <div
                  key={step.id}
                  className={`flex items-center gap-3 transition-all duration-300 ${
                    isCurrent ? 'opacity-100' : isPending ? 'opacity-40' : 'opacity-70'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="h-5 w-5 text-primary animate-spin flex-shrink-0" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-300 flex-shrink-0" />
                  )}
                  <span
                    className={`text-sm ${
                      isCurrent
                        ? 'font-semibold text-gray-900'
                        : isCompleted
                        ? 'text-gray-700'
                        : 'text-gray-500'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Please do not close this window while we process your data
        </p>
      </div>
    </div>
  );
}
