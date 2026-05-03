import { useState } from 'react';

interface ProfileSetupData {
  age: number;
  height_cm: number;
  gender: string;
  is_pregnant: boolean;
  allergens: string[];
  health_conditions: string[];
}

interface ProfileSetupModalProps {
  onComplete: (data: ProfileSetupData) => void;
}

const COMMON_ALLERGENS = [
  'Peanuts',
  'Tree Nuts',
  'Milk',
  'Eggs',
  'Wheat',
  'Soy',
  'Fish',
  'Shellfish',
];

const COMMON_HEALTH_CONDITIONS = [
  'Hypertension',
  'High Cholesterol',
  'Heart Disease',
  'Kidney Disease',
  'Thyroid Disorder',
  'Celiac Disease',
];

export default function ProfileSetupModal({ onComplete }: ProfileSetupModalProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<ProfileSetupData>({
    age: 0,
    height_cm: 0,
    gender: '',
    is_pregnant: false,
    allergens: [],
    health_conditions: [],
  });

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      onComplete(formData);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const toggleAllergen = (allergen: string) => {
    setFormData(prev => ({
      ...prev,
      allergens: prev.allergens.includes(allergen)
        ? prev.allergens.filter(a => a !== allergen)
        : [...prev.allergens, allergen],
    }));
  };

  const toggleHealthCondition = (condition: string) => {
    setFormData(prev => ({
      ...prev,
      health_conditions: prev.health_conditions.includes(condition)
        ? prev.health_conditions.filter(c => c !== condition)
        : [...prev.health_conditions, condition],
    }));
  };

  const isStepValid = () => {
    if (step === 1) return formData.age > 0 && formData.height_cm > 0 && formData.gender !== '';
    return true; // Steps 2 and 3 are optional
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Complete Your Profile</h2>
            <p className="text-sm text-gray-600 mt-1">Step {step} of 3 - Required for health tracking</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-6 pt-4">
          <div className="flex gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  s <= step ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6">
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Basic Information
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  This information will be used for your health assessments.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Age <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={formData.age || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, age: parseInt(e.target.value) || 0 })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your age"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Height (cm) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="50"
                    max="250"
                    value={formData.height_cm || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, height_cm: parseInt(e.target.value) || 0 })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your height"
                  />
                </div>
              </div>

              {/* Gender Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Gender <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {['Male', 'Female', 'Other'].map((gender) => (
                    <button
                      key={gender}
                      type="button"
                      onClick={() => {
                        setFormData({ ...formData, gender, is_pregnant: false });
                      }}
                      className={`px-4 py-3 rounded-lg border-2 text-center transition-all ${
                        formData.gender === gender
                          ? 'border-blue-600 bg-blue-50 text-blue-900'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {gender}
                    </button>
                  ))}
                </div>
              </div>

              {/* Pregnancy Toggle (only for females) */}
              {formData.gender === 'Female' && (
                <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                  <label className="flex items-center justify-between cursor-pointer">
                    <div>
                      <span className="text-sm font-medium text-gray-900">Currently Pregnant</span>
                      <p className="text-xs text-gray-600 mt-1">
                        This helps us provide better health tracking
                      </p>
                    </div>
                    <div className="relative">
                      <input
                        type="checkbox"
                        checked={formData.is_pregnant}
                        onChange={(e) =>
                          setFormData({ ...formData, is_pregnant: e.target.checked })
                        }
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </div>
                  </label>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Allergen Info */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Allergen Information
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Select any food allergens you have. This helps us provide safer meal recommendations.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {COMMON_ALLERGENS.map((allergen) => (
                  <button
                    key={allergen}
                    onClick={() => toggleAllergen(allergen)}
                    className={`px-4 py-3 rounded-lg border-2 text-left transition-all ${
                      formData.allergens.includes(allergen)
                        ? 'border-blue-600 bg-blue-50 text-blue-900'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {allergen}
                  </button>
                ))}
              </div>

              <p className="text-xs text-gray-500 mt-4">
                You can skip this step and add allergens later in your profile settings.
              </p>
            </div>
          )}

          {/* Step 3: Health Conditions */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Health Conditions
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  Select any existing health conditions. This information helps personalize your health tracking.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {COMMON_HEALTH_CONDITIONS.map((condition) => (
                  <button
                    key={condition}
                    onClick={() => toggleHealthCondition(condition)}
                    className={`px-4 py-3 rounded-lg border-2 text-left transition-all ${
                      formData.health_conditions.includes(condition)
                        ? 'border-blue-600 bg-blue-50 text-blue-900'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    {condition}
                  </button>
                ))}
              </div>

              <p className="text-xs text-gray-500 mt-4">
                You can skip this step and add health conditions later in your profile settings.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 flex items-center justify-between border-t">
          <button
            onClick={handleBack}
            disabled={step === 1}
            className="px-4 py-2 text-gray-700 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={!isStepValid()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {step === 3 ? 'Complete Setup' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
}
