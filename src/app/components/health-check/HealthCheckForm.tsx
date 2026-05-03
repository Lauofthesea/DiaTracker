import React, { useState, useEffect } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Card, CardContent } from '@/app/components/ui/card';
import { Loader2, Info } from 'lucide-react';
import { validateHealthMetrics, calculateBMI, getBMICategory, HealthCheckSubmitRequest } from '@/lib/healthCheck';

interface HealthCheckFormProps {
  onSubmit: (data: HealthCheckSubmitRequest) => void;
  error?: string;
  initialData?: Partial<HealthCheckSubmitRequest>;
  showSubmitButton?: boolean;
}

const SYMPTOMS = [
  { id: 'frequent_urination', label: 'Frequent urination' },
  { id: 'excessive_thirst', label: 'Excessive thirst' },
  { id: 'fatigue', label: 'Unusual fatigue' },
  { id: 'blurred_vision', label: 'Blurred vision' },
  { id: 'slow_healing', label: 'Slow healing of wounds' },
  { id: 'tingling_hands_feet', label: 'Tingling in hands or feet' },
  { id: 'unexplained_weight_loss', label: 'Unexplained weight loss' },
  { id: 'increased_hunger', label: 'Increased hunger' },
  { id: 'dry_skin', label: 'Dry skin' },
  { id: 'frequent_infections', label: 'Frequent infections' },
];

export default function HealthCheckForm({ 
  onSubmit, 
  error, 
  initialData,
  showSubmitButton = true 
}: HealthCheckFormProps) {
  const [weight, setWeight] = useState(initialData?.weight?.toString() || '');
  const [weightUnit, setWeightUnit] = useState<'kg' | 'lbs'>(initialData?.weight_unit || 'kg');
  const [bloodSugar, setBloodSugar] = useState(initialData?.blood_sugar?.toString() || '');
  const [age, setAge] = useState(initialData?.age?.toString() || '');
  const [height, setHeight] = useState(initialData?.height?.toString() || '');
  const [heightUnit, setHeightUnit] = useState<'cm' | 'in'>(initialData?.height_unit || 'cm');
  const [symptoms, setSymptoms] = useState<string[]>(initialData?.symptoms || []);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [bmi, setBmi] = useState<number | null>(null);

  // Calculate BMI when weight or height changes
  useEffect(() => {
    const w = parseFloat(weight);
    const h = parseFloat(height);
    if (!isNaN(w) && !isNaN(h) && w > 0 && h > 0) {
      const calculatedBmi = calculateBMI(w, weightUnit, h, heightUnit);
      setBmi(calculatedBmi);
    } else {
      setBmi(null);
    }
  }, [weight, weightUnit, height, heightUnit]);

  const handleSymptomToggle = (symptomId: string) => {
    setSymptoms((prev) =>
      prev.includes(symptomId)
        ? prev.filter((s) => s !== symptomId)
        : [...prev, symptomId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationErrors([]);

    const data: HealthCheckSubmitRequest = {
      weight: parseFloat(weight),
      weight_unit: weightUnit,
      blood_sugar: parseFloat(bloodSugar),
      age: parseInt(age, 10),
      height: parseFloat(height),
      height_unit: heightUnit,
      symptoms,
    };

    // Validate data
    const validation = validateHealthMetrics(data);
    if (!validation.valid) {
      setValidationErrors(validation.errors);
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 py-4">
      {(error || validationErrors.length > 0) && (
        <Alert variant="destructive">
          <AlertDescription>
            {error || validationErrors.join('. ')}
          </AlertDescription>
        </Alert>
      )}

      {/* Weight Input */}
      <div className="space-y-2">
        <Label htmlFor="weight">Weight *</Label>
        <div className="flex gap-2">
          <Input
            id="weight"
            type="number"
            step="0.1"
            placeholder="Enter weight"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            required
            className="flex-1"
          />
          <Select value={weightUnit} onValueChange={(value: 'kg' | 'lbs') => setWeightUnit(value)}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="kg">kg</SelectItem>
              <SelectItem value="lbs">lbs</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Height Input */}
      <div className="space-y-2">
        <Label htmlFor="height">Height *</Label>
        <div className="flex gap-2">
          <Input
            id="height"
            type="number"
            step="0.1"
            placeholder="Enter height"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            required
            className="flex-1"
          />
          <Select value={heightUnit} onValueChange={(value: 'cm' | 'in') => setHeightUnit(value)}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="cm">cm</SelectItem>
              <SelectItem value="in">in</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* BMI Display */}
      {bmi !== null && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">
                Calculated BMI: {bmi.toFixed(1)} ({getBMICategory(bmi)})
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Blood Sugar Input */}
      <div className="space-y-2">
        <Label htmlFor="bloodSugar">Blood Sugar (mg/dL) *</Label>
        <Input
          id="bloodSugar"
          type="number"
          step="0.1"
          placeholder="Enter blood sugar level"
          value={bloodSugar}
          onChange={(e) => setBloodSugar(e.target.value)}
          required
        />
        <p className="text-xs text-gray-500">Normal fasting: 70-100 mg/dL</p>
      </div>

      {/* Age Input */}
      <div className="space-y-2">
        <Label htmlFor="age">Age (years) *</Label>
        <Input
          id="age"
          type="number"
          placeholder="Enter age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
        />
      </div>

      {/* Symptoms Checklist */}
      <div className="space-y-3">
        <Label>Symptoms (select all that apply)</Label>
        <div className="space-y-2">
          {SYMPTOMS.map((symptom) => (
            <div key={symptom.id} className="flex items-center space-x-2">
              <Checkbox
                id={symptom.id}
                checked={symptoms.includes(symptom.id)}
                onCheckedChange={() => handleSymptomToggle(symptom.id)}
              />
              <label
                htmlFor={symptom.id}
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
              >
                {symptom.label}
              </label>
            </div>
          ))}
        </div>
      </div>

      {showSubmitButton && (
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            'Continue to Consent'
          )}
        </Button>
      )}
    </form>
  );
}
