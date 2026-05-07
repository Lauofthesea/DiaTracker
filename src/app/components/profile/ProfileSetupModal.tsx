import { useState } from 'react';

interface ProfileSetupData {
  age: number;
  height_cm: number;
  weight_kg: number;
  gender: string;
  is_pregnant: boolean;
  has_family_history: boolean;
}

interface ProfileSetupModalProps {
  onComplete: (data: ProfileSetupData) => void;
}

export default function ProfileSetupModal({ onComplete }: ProfileSetupModalProps) {
  const [formData, setFormData] = useState<ProfileSetupData>({
    age: 0,
    height_cm: 0,
    weight_kg: 0,
    gender: '',
    is_pregnant: false,
    has_family_history: false,
  });

  const handleComplete = () => {
    onComplete(formData);
  };

  const isFormValid = () => {
    return formData.age > 0 && formData.height_cm > 0 && formData.weight_kg > 0 && formData.gender !== '';
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Complete Your Profile</h2>
            <p className="text-sm text-gray-600 mt-1">Required for health tracking</p>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6">
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
                    Weight (kg) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    min="20"
                    max="300"
                    step="0.1"
                    value={formData.weight_kg || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, weight_kg: parseFloat(e.target.value) || 0 })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your weight"
                  />
                </div>

                <div className="col-span-2">
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
                <div className="grid grid-cols-2 gap-3">
                  {['Male', 'Female'].map((gender) => (
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

              {/* Family History Toggle */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <span className="text-sm font-medium text-gray-900">Family History of Diabetes</span>
                    <p className="text-xs text-gray-600 mt-1">
                      Do you have parents or siblings with diabetes?
                    </p>
                  </div>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={formData.has_family_history}
                      onChange={(e) =>
                        setFormData({ ...formData, has_family_history: e.target.checked })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </div>
                </label>
              </div>
            </div>
          </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 px-6 py-4 flex items-center justify-end border-t">
          <button
            onClick={handleComplete}
            disabled={!isFormValid()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Complete Setup
          </button>
        </div>
      </div>
    </div>
  );
}
