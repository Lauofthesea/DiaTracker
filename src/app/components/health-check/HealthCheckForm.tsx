import React, { useState, useEffect } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Alert, AlertDescription } from '@/app/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/ui/select';
import { Loader2 } from 'lucide-react';
import { validateHealthMetrics, HealthCheckSubmitRequest } from '@/lib/healthCheck';

interface HealthCheckFormProps {
  onSubmit: (data: HealthCheckSubmitRequest) => void;
  error?: string;
  initialData?: Partial<HealthCheckSubmitRequest>;
  showSubmitButton?: boolean;
  profileData?: { age: number | null; height_cm: number | null };
  lastHealthCheck?: { weight_kg: number; blood_sugar_mgdl: number } | null;
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
  showSubmitButton = true,
  profileData,
  lastHealthCheck
}: HealthCheckFormProps) {
  const [weight, setWeight] = useState(
    lastHealthCheck?.weight_kg?.toString() || initialData?.weight?.toString() || ''
  );
  const [weightUnit, setWeightUnit] = useState<'kg' | 'lbs'>(initialData?.weight_unit || 'kg');
  const [bloodSugar, setBloodSugar] = useState(
    lastHealthCheck?.blood_sugar_mgdl?.toString() || initialData?.blood_sugar?.toString() || ''
  );
  const [age, setAge] = useState(
    profileData?.age?.toString() || initialData?.age?.toString() || ''
  );
  const [height, setHeight] = useState(
    profileData?.height_cm?.toString() || initialData?.height?.toString() || ''
  );
  const [heightUnit, setHeightUnit] = useState<'cm' | 'in'>(initialData?.height_unit || 'cm');
  const [symptoms, setSymptoms] = useState<string[]>(initialData?.symptoms || []);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isAgePreFilled = !!profileData?.age;
  const isHeightPreFilled = !!profileData?.height_cm;
  const isWeightPreFilled = !!lastHealthCheck?.weight_kg;
  const isBloodSugarPreFilled = !!lastHealthCheck?.blood_sugar_mgdl;

  useEffect(() => {
    if (profileData?.age && !age) {
      setAge(profileData.age.toString());
    }
  }, [profileData?.age]);

  useEffect(() => {
    if (profileData?.height_cm && !height) {
      setHeight(profileData.height_cm.toString());
    }
  }, [profileData?.height_cm]);

  useEffect(() => {
    if (lastHealthCheck?.weight_kg && !weight) {
      setWeight(lastHealthCheck.weight_kg.toString());
    }
  }, [lastHealthCheck?.weight_kg]);

  useEffect(() => {
    if (lastHealthCheck?.blood_sugar_mgdl && !bloodSugar) {
      setBloodSugar(lastHealthCheck.blood_sugar_mgdl.toString());
    }
  }, [lastHealthCheck?.blood_sugar_mgdl]);

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
        <Label htmlFor="weight">
          Weight *
          {isWeightPreFilled && (
            <span className="ml-2 text-xs text-blue-600 font-normal">
              (based from last check)
            </span>
          )}
        </Label>
        <div className="flex gap-2">
          <Input
            id="weight"
            type="number"
            step="0.1"
            placeholder="Enter weight"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            required
            className={`flex-1 ${isWeightPreFilled ? 'border-blue-300 bg-blue-50/30' : ''}`}
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
        {isWeightPreFilled && (
          <p className="text-xs text-blue-600">
            Value from your last health check. You can edit if needed.
          </p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="bloodSugar">
          Blood Sugar (mg/dL) *
          {isBloodSugarPreFilled && (
            <span className="ml-2 text-xs text-blue-600 font-normal">
              (based from last check)
            </span>
          )}
        </Label>
        <Input
          id="bloodSugar"
          type="number"
          step="0.1"
          placeholder="Enter blood sugar level"
          value={bloodSugar}
          onChange={(e) => setBloodSugar(e.target.value)}
          required
          className={isBloodSugarPreFilled ? 'border-blue-300 bg-blue-50/30' : ''}
        />
        {isBloodSugarPreFilled ? (
          <p className="text-xs text-blue-600">
            Value from your last health check. You can edit if needed.
          </p>
        ) : (
          <p className="text-xs text-gray-500">Normal fasting: 70-100 mg/dL</p>
        )}
      </div>

      {(isAgePreFilled || isHeightPreFilled) && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
          <p className="text-sm font-medium text-gray-700">
            Information from your profile:
          </p>
          
          {isAgePreFilled && (
            <div className="space-y-2">
              <Label htmlFor="age" className="text-gray-600">Age (years)</Label>
              <Input
                id="age"
                type="number"
                value={age}
                readOnly
                className="bg-gray-100 text-gray-600 cursor-not-allowed"
              />
            </div>
          )}

          {isHeightPreFilled && (
            <div className="space-y-2">
              <Label htmlFor="height" className="text-gray-600">Height</Label>
              <div className="flex gap-2">
                <Input
                  id="height"
                  type="number"
                  step="0.1"
                  value={height}
                  readOnly
                  className="flex-1 bg-gray-100 text-gray-600 cursor-not-allowed"
                />
                <Select value={heightUnit} disabled>
                  <SelectTrigger className="w-24 bg-gray-100 text-gray-600 cursor-not-allowed">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cm">cm</SelectItem>
                    <SelectItem value="in">in</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
        </div>
      )}

      {!isAgePreFilled && (
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
      )}

      {!isHeightPreFilled && (
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
      )}

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
