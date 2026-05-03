import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/app/components/ui/card';
import { Progress } from '@/app/components/ui/progress';
import { Loader2, CheckCircle2 } from 'lucide-react';

interface ProcessingIndicatorProps {
  hasMealsInLast24Hours?: boolean;
}

const BASE_PROCESSING_STEPS = [
  { id: 1, label: 'Validating health metrics', duration: 4000 },
  { id: 2, label: 'Preprocessing data', duration: 4000 },
  { id: 3, label: 'Loading ML model', duration: 4000 },
  { id: 4, label: 'Analyzing patterns', duration: 4000 },
  { id: 5, label: 'Calculating confidence scores', duration: 4000 },
  { id: 6, label: 'Generating prediction', duration: 4000 },
];

const MEAL_CHECK_STEP = { id: 7, label: 'Checking logged meals', duration: 4000 };

export default function ProcessingIndicator({ hasMealsInLast24Hours = false }: ProcessingIndicatorProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  // Add meal checking step if user has meals in last 24 hours
  const PROCESSING_STEPS = hasMealsInLast24Hours 
    ? [...BASE_PROCESSING_STEPS.slice(0, 3), MEAL_CHECK_STEP, ...BASE_PROCESSING_STEPS.slice(3)]
    : BASE_PROCESSING_STEPS;

  useEffect(() => {
    let stepTimer: ReturnType<typeof setTimeout>;

    const startNextStep = (stepIndex: number) => {
      if (stepIndex >= PROCESSING_STEPS.length) {
        setProgress(100);
        return;
      }

      setCurrentStep(stepIndex);
      const step = PROCESSING_STEPS[stepIndex];
      
      // Calculate progress for this step
      const progressPerStep = 100 / PROCESSING_STEPS.length;
      const targetProgress = (stepIndex + 1) * progressPerStep;
      
      // Smoothly animate to target progress
      const startProgress = stepIndex * progressPerStep;
      const duration = step.duration;
      const startTime = Date.now();
      
      const animateProgress = () => {
        const elapsed = Date.now() - startTime;
        const progressRatio = Math.min(elapsed / duration, 1);
        const currentProgress = startProgress + (targetProgress - startProgress) * progressRatio;
        
        setProgress(currentProgress);
        
        if (progressRatio < 1) {
          requestAnimationFrame(animateProgress);
        }
      };
      
      animateProgress();

      // Move to next step after duration
      stepTimer = setTimeout(() => {
        setProgress(targetProgress); // Ensure exact progress
        startNextStep(stepIndex + 1);
      }, step.duration);
    };

    startNextStep(0);

    return () => {
      clearTimeout(stepTimer);
    };
  }, [hasMealsInLast24Hours]);

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
