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
  profileData?: { 
    age: number | null; 
    height_cm: number | null;
    weight_kg: number | null;
    gender: string | null;
    family_history: boolean | null;
  };
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
  const [weight, setWeight] = useState('');
  const [weightUnit, setWeightUnit] = useState<'kg' | 'lbs'>(initialData?.weight_unit || 'kg');
  const [bloodSugar, setBloodSugar] = useState(
    lastHealthCheck?.blood_sugar_mgdl?.toString() || initialData?.blood_sugar?.toString() || ''
  );
  const [age, setAge] = useState('');
  const [height, setHeight] = useState('');
  const [heightUnit, setHeightUnit] = useState<'cm' | 'in'>(initialData?.height_unit || 'cm');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isAgePreFilled = !!profileData?.age;
  const isHeightPreFilled = !!profileData?.height_cm;
  const isWeightPreFilled = !!profileData?.weight_kg;
  const isBloodSugarPreFilled = !!lastHealthCheck?.blood_sugar_mgdl;

  // Set initial values from profile data
  useEffect(() => {
    if (profileData?.age) {
      setAge(profileData.age.toString());
    }
  }, [profileData?.age]);

  useEffect(() => {
    if (profileData?.height_cm) {
      setHeight(profileData.height_cm.toString());
    }
  }, [profileData?.height_cm]);

  useEffect(() => {
    if (profileData?.weight_kg) {
      setWeight(profileData.weight_kg.toString());
    }
  }, [profileData?.weight_kg]);

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
      symptoms: [], // No symptoms collected
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

      {/* Info banner if any data is pre-filled from profile */}
      {(isWeightPreFilled || isAgePreFilled || isHeightPreFilled) && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 -mt-2">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">Note:</span> Some fields below are pre-filled from your profile. You can edit any value if needed.
          </p>
        </div>
      )}

      {/* Blood Sugar Input - First */}
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
          className={isBloodSugarPreFilled ? 'border-blue-300 bg-blue-50/30' : ''}
        />
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
            className={`flex-1 ${isHeightPreFilled ? 'border-blue-300 bg-blue-50/30' : ''}`}
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
      </div>

      {/* Gender and Age in one row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Gender - Read Only */}
        <div className="space-y-2">
          <Label htmlFor="gender">Gender</Label>
          <Input
            id="gender"
            type="text"
            value={profileData?.gender || 'Not specified'}
            readOnly
            className="bg-gray-100 text-gray-700 cursor-not-allowed"
          />
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
            className={isAgePreFilled ? 'border-blue-300 bg-blue-50/30' : ''}
          />
        </div>
      </div>

      {/* Family History - Read Only with note */}
      {profileData?.family_history !== null && profileData?.family_history !== undefined && (
        <div className="space-y-2">
          <Label htmlFor="familyHistory">Family History of Diabetes</Label>
          <div className="relative">
            <Input
              id="familyHistory"
              type="text"
              value={profileData.family_history ? 'Yes' : 'No'}
              readOnly
              className="bg-gray-100 text-gray-700 cursor-not-allowed"
            />
          </div>
          {profileData.family_history && (
            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1.5">
              ⚠️ Having a family history of diabetes increases your risk. This is considered in your assessment.
            </p>
          )}
        </div>
      )}

      {showSubmitButton && (
        <Button type="submit" className="w-full mt-4" disabled={isSubmitting}>
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
