import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, User, Edit2, Save, X, Loader2, AlertCircle, CheckCircle2, LogOut } from "lucide-react";
import ResponsiveLayout from "./ResponsiveLayout";
import { useAuth } from "../contexts/AuthContext";
import { getProfile, updateProfile, getHealthMetricsHistory } from "../../lib/profileApi";
import type { ProfileResponse, HealthMetricsHistoryItem } from "../../types/profile";

export default function ProfilePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedName, setEditedName] = useState("");
  const [editedAllergens, setEditedAllergens] = useState<string[]>([]);
  const [editedDietaryRestrictions, setEditedDietaryRestrictions] = useState<string[]>([]);
  const [editedHealthConditions, setEditedHealthConditions] = useState<string[]>([]);
  
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  
  const [metricsHistory, setMetricsHistory] = useState<HealthMetricsHistoryItem[]>([]);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotalPages, setHistoryTotalPages] = useState(1);
  const [loadingHistory, setLoadingHistory] = useState(false);
  
  // Validation errors
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Common allergens
  const commonAllergens = ["Dairy", "Nuts", "Shellfish", "Soy", "Eggs", "Wheat", "Fish", "Peanuts"];
  
  // Common dietary restrictions
  const commonDietaryRestrictions = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Pescatarian", "Keto", "Paleo"];
  
  // Common health conditions
  const commonHealthConditions = ["Type 1 Diabetes", "Type 2 Diabetes", "Hypertension", "High Cholesterol", "Heart Disease"];

  // Load profile data on mount
  useEffect(() => {
    loadProfile();
    loadHealthMetricsHistory();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getProfile();
      setProfile(data);
      
      // Initialize edit state with current values
      setEditedName(data.name);
      setEditedAllergens(data.allergen_preferences || []);
      setEditedDietaryRestrictions(data.dietary_restrictions || []);
      setEditedHealthConditions(data.health_conditions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const loadHealthMetricsHistory = async (page: number = 1) => {
    try {
      setLoadingHistory(true);
      const data = await getHealthMetricsHistory(page, 5);
      setMetricsHistory(data.metrics);
      setHistoryPage(data.page);
      setHistoryTotalPages(data.total_pages);
    } catch (err) {
      console.error("Failed to load health metrics history:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    
    if (!editedName.trim()) {
      errors.name = "Name is required";
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const updateData = {
        name: editedName.trim(),
        allergen_preferences: editedAllergens,
        dietary_restrictions: editedDietaryRestrictions,
        health_conditions: editedHealthConditions,
      };
      
      const updatedProfile = await updateProfile(updateData);
      setProfile(updatedProfile);
      setIsEditMode(false);
      setSuccessMessage("Profile updated successfully!");
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    if (profile) {
      setEditedName(profile.name);
      setEditedAllergens(profile.allergen_preferences || []);
      setEditedDietaryRestrictions(profile.dietary_restrictions || []);
      setEditedHealthConditions(profile.health_conditions || []);
    }
    setIsEditMode(false);
    setValidationErrors({});
  };

  const toggleArrayItem = (array: string[], item: string, setter: (arr: string[]) => void) => {
    if (array.includes(item)) {
      setter(array.filter(i => i !== item));
    } else {
      setter([...array, item]);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const inputClass = "w-full h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none text-[#0d2b35] placeholder:text-[rgba(13,43,53,0.5)]";

  if (loading) {
    return (
      <ResponsiveLayout>
        <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <Loader2 size={40} className="text-[#1e6177] animate-spin" />
            <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
              Loading profile...
            </p>
          </div>
        </div>
      </ResponsiveLayout>
    );
  }

  if (error && !profile) {
    return (
      <ResponsiveLayout>
        <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto flex items-center justify-center px-6">
          <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 w-full max-w-md">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle size={24} className="text-red-500" />
              <p className="text-[16px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                Error Loading Profile
              </p>
            </div>
            <p className="text-[14px] text-[#637c84] mb-4" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
              {error}
            </p>
            <button
              onClick={loadProfile}
              className="w-full h-[48px] bg-[#1e6177] text-white rounded-xl border-none cursor-pointer text-[14px]"
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
            >
              Try Again
            </button>
          </div>
        </div>
      </ResponsiveLayout>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <ResponsiveLayout>
      <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto relative">
        
        <div className="sticky top-0 z-40 backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-b-[0.8px] border-solid border-[rgba(226,234,235,0.4)] px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate("/")}
                className="bg-[rgba(226,234,235,0.5)] rounded-full w-10 h-10 flex items-center justify-center cursor-pointer border-none md:hidden"
              >
                <ArrowLeft size={24} className="text-[#0d2b35]" />
              </button>
              <p className="text-[20px] text-[#0d2b35] tracking-[-0.5px]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                Profile
              </p>
            </div>
            {!isEditMode && (
              <button
                onClick={() => setIsEditMode(true)}
                className="bg-[rgba(30,97,119,0.1)] rounded-full w-10 h-10 flex items-center justify-center cursor-pointer border-none"
              >
                <Edit2 size={20} className="text-[#1e6177]" />
              </button>
            )}
          </div>
        </div>

      
      {successMessage && (
        <div className="mx-6 mt-4 bg-green-50 border-[0.8px] border-green-200 rounded-2xl p-4 flex items-center gap-3">
          <CheckCircle2 size={20} className="text-green-600" />
          <p className="text-[14px] text-green-800" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
            {successMessage}
          </p>
        </div>
      )}

      
      {error && (
        <div className="mx-6 mt-4 bg-red-50 border-[0.8px] border-red-200 rounded-2xl p-4 flex items-center gap-3">
          <AlertCircle size={20} className="text-red-600" />
          <p className="text-[14px] text-red-800" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
            {error}
          </p>
        </div>
      )}

      <div className="px-6 pt-6 pb-[100px]">
        
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 flex flex-col items-center mb-4">
          <div className="w-20 h-20 rounded-full bg-[rgba(30,97,119,0.1)] flex items-center justify-center mb-3">
            <User size={40} className="text-[#1e6177]" />
          </div>
          {isEditMode ? (
            <div className="w-full">
              <input
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className={`${inputClass} text-center ${validationErrors.name ? 'border-red-500' : ''}`}
                placeholder="Enter your name"
              />
              {validationErrors.name && (
                <p className="text-[12px] text-red-500 mt-1 text-center" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  {validationErrors.name}
                </p>
              )}
            </div>
          ) : (
            <>
              <p className="text-[18px] text-[#0d2b35] mb-1" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                {profile.name}
              </p>
              <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                {profile.email}
              </p>
            </>
          )}
        </div>

        
        {profile.current_health_metrics && (
          <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 mb-4">
            <p className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-5" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
              Current Health Metrics
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[rgba(226,234,235,0.2)] rounded-2xl p-4">
                <p className="text-[12px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                  Weight
                </p>
                <p className="text-[20px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                  {profile.current_health_metrics.weight_kg.toFixed(1)} <span className="text-[12px] text-[#637c84]">kg</span>
                </p>
              </div>
              <div className="bg-[rgba(226,234,235,0.2)] rounded-2xl p-4">
                <p className="text-[12px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                  Blood Sugar
                </p>
                <p className="text-[20px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                  {profile.current_health_metrics.blood_sugar_mgdl.toFixed(0)} <span className="text-[12px] text-[#637c84]">mg/dL</span>
                </p>
              </div>
              <div className="bg-[rgba(226,234,235,0.2)] rounded-2xl p-4">
                <p className="text-[12px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                  Age
                </p>
                <p className="text-[20px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                  {profile.age || profile.current_health_metrics.age} <span className="text-[12px] text-[#637c84]">years</span>
                </p>
              </div>
              <div className="bg-[rgba(226,234,235,0.2)] rounded-2xl p-4">
                <p className="text-[12px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                  Height
                </p>
                <p className="text-[20px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                  {profile.height_cm || profile.current_health_metrics.height_cm.toFixed(0)} <span className="text-[12px] text-[#637c84]">cm</span>
                </p>
              </div>
              <div className="bg-[rgba(226,234,235,0.2)] rounded-2xl p-4 col-span-2">
                <p className="text-[12px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                  BMI
                </p>
                <p className="text-[20px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                  {profile.current_health_metrics.bmi.toFixed(1)}
                </p>
              </div>
            </div>
            <p className="text-[12px] text-[#637c84] mt-4" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
              Last updated: {formatDate(profile.current_health_metrics.recorded_at)}
            </p>
          </div>
        )}

        
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 mb-4">
          <p className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-5" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
            Allergen Preferences
          </p>
          {isEditMode ? (
            <div className="flex flex-wrap gap-2">
              {commonAllergens.map((allergen) => (
                <button
                  key={allergen}
                  onClick={() => toggleArrayItem(editedAllergens, allergen, setEditedAllergens)}
                  className={`px-4 py-2 rounded-xl border-[0.8px] text-[14px] cursor-pointer ${
                    editedAllergens.includes(allergen)
                      ? "bg-[rgba(30,97,119,0.1)] border-[#1e6177] text-[#1e6177]"
                      : "bg-[rgba(226,234,235,0.1)] border-[rgba(226,234,235,0.3)] text-[#637c84]"
                  }`}
                  style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                >
                  {allergen}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.allergen_preferences && profile.allergen_preferences.length > 0 ? (
                profile.allergen_preferences.map((allergen) => (
                  <span
                    key={allergen}
                    className="px-4 py-2 rounded-xl bg-[rgba(30,97,119,0.1)] border-[0.8px] border-[#1e6177] text-[#1e6177] text-[14px]"
                    style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                  >
                    {allergen}
                  </span>
                ))
              ) : (
                <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  No allergen preferences set
                </p>
              )}
            </div>
          )}
        </div>

        
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 mb-4">
          <p className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-5" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
            Dietary Restrictions
          </p>
          {isEditMode ? (
            <div className="flex flex-wrap gap-2">
              {commonDietaryRestrictions.map((restriction) => (
                <button
                  key={restriction}
                  onClick={() => toggleArrayItem(editedDietaryRestrictions, restriction, setEditedDietaryRestrictions)}
                  className={`px-4 py-2 rounded-xl border-[0.8px] text-[14px] cursor-pointer ${
                    editedDietaryRestrictions.includes(restriction)
                      ? "bg-[rgba(30,97,119,0.1)] border-[#1e6177] text-[#1e6177]"
                      : "bg-[rgba(226,234,235,0.1)] border-[rgba(226,234,235,0.3)] text-[#637c84]"
                  }`}
                  style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                >
                  {restriction}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.dietary_restrictions && profile.dietary_restrictions.length > 0 ? (
                profile.dietary_restrictions.map((restriction) => (
                  <span
                    key={restriction}
                    className="px-4 py-2 rounded-xl bg-[rgba(30,97,119,0.1)] border-[0.8px] border-[#1e6177] text-[#1e6177] text-[14px]"
                    style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                  >
                    {restriction}
                  </span>
                ))
              ) : (
                <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  No dietary restrictions set
                </p>
              )}
            </div>
          )}
        </div>

        
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 mb-4">
          <p className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-5" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
            Health Conditions
          </p>
          {isEditMode ? (
            <div className="flex flex-wrap gap-2">
              {commonHealthConditions.map((condition) => (
                <button
                  key={condition}
                  onClick={() => toggleArrayItem(editedHealthConditions, condition, setEditedHealthConditions)}
                  className={`px-4 py-2 rounded-xl border-[0.8px] text-[14px] cursor-pointer ${
                    editedHealthConditions.includes(condition)
                      ? "bg-[rgba(30,97,119,0.1)] border-[#1e6177] text-[#1e6177]"
                      : "bg-[rgba(226,234,235,0.1)] border-[rgba(226,234,235,0.3)] text-[#637c84]"
                  }`}
                  style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                >
                  {condition}
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {profile.health_conditions && profile.health_conditions.length > 0 ? (
                profile.health_conditions.map((condition) => (
                  <span
                    key={condition}
                    className="px-4 py-2 rounded-xl bg-[rgba(30,97,119,0.1)] border-[0.8px] border-[#1e6177] text-[#1e6177] text-[14px]"
                    style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
                  >
                    {condition}
                  </span>
                ))
              ) : (
                <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  No health conditions set
                </p>
              )}
            </div>
          )}
        </div>

        
        {!isEditMode && metricsHistory.length > 0 && (
          <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6 mb-6">
            <p className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-5" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
              Health Metrics History
            </p>
            <div className="space-y-4">
              {metricsHistory.map((metric) => (
                <div key={metric.metric_id} className="bg-[rgba(226,234,235,0.1)] rounded-2xl p-4">
                  <div className="flex justify-between items-start mb-3">
                    <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                      {formatDate(metric.recorded_at)}
                    </p>
                    {metric.prediction && (
                      <span className={`px-3 py-1 rounded-lg text-[12px] ${
                        metric.prediction.classification === "No Diabetes"
                          ? "bg-green-100 text-green-800"
                          : metric.prediction.classification === "Type 1"
                          ? "bg-orange-100 text-orange-800"
                          : "bg-red-100 text-red-800"
                      }`} style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}>
                        {metric.prediction.classification}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div>
                      <p className="text-[10px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>Weight</p>
                      <p className="text-[14px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                        {metric.weight_kg.toFixed(1)} kg
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>Blood Sugar</p>
                      <p className="text-[14px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                        {metric.blood_sugar_mgdl.toFixed(0)} mg/dL
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-[#637c84] mb-1" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>BMI</p>
                      <p className="text-[14px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                        {metric.bmi.toFixed(1)}
                      </p>
                    </div>
                  </div>
                  {metric.prediction && (
                    <div className="mt-3 pt-3 border-t border-[rgba(226,234,235,0.3)]">
                      <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                        Confidence: <span className="font-semibold text-[#0d2b35]">{(metric.prediction.confidence * 100).toFixed(1)}%</span>
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
            {historyTotalPages > 1 && (
              <div className="flex justify-between items-center mt-4">
                <button
                  onClick={() => loadHealthMetricsHistory(historyPage - 1)}
                  disabled={historyPage === 1 || loadingHistory}
                  className="px-4 py-2 rounded-xl bg-[rgba(226,234,235,0.5)] text-[#0d2b35] text-[14px] border-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
                >
                  Previous
                </button>
                <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  Page {historyPage} of {historyTotalPages}
                </p>
                <button
                  onClick={() => loadHealthMetricsHistory(historyPage + 1)}
                  disabled={historyPage === historyTotalPages || loadingHistory}
                  className="px-4 py-2 rounded-xl bg-[rgba(226,234,235,0.5)] text-[#0d2b35] text-[14px] border-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}

        
        {isEditMode && (
          <div className="flex gap-3">
            <button
              onClick={handleCancelEdit}
              disabled={saving}
              className="flex-1 h-[56px] bg-[rgba(226,234,235,0.5)] text-[#0d2b35] rounded-2xl border-none cursor-pointer text-[16px] flex items-center justify-center gap-2 disabled:opacity-50"
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
            >
              <X size={20} />
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 h-[56px] bg-[#1e6177] text-white rounded-2xl border-none cursor-pointer shadow-sm text-[16px] flex items-center justify-center gap-2 disabled:opacity-50"
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
            >
              {saving ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={20} />
                  Save Changes
                </>
              )}
            </button>
          </div>
        )}

        {!isEditMode && (
          <button
            onClick={() => setShowLogoutModal(true)}
            disabled={isLoggingOut}
            className="w-full h-[56px] bg-transparent border-[0.8px] border-[rgba(239,68,68,0.3)] text-[#ef4444] rounded-2xl cursor-pointer text-[16px] flex items-center justify-center gap-2 hover:bg-[rgba(239,68,68,0.05)] transition-colors mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
          >
            {isLoggingOut ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Logging out...
              </>
            ) : (
              <>
                <LogOut size={20} />
                Logout
              </>
            )}
          </button>
        )}
      </div>

      {showLogoutModal && (
        <div
          className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center px-4"
          onClick={() => setShowLogoutModal(false)}
        >
          <div
            className="bg-white rounded-3xl w-full max-w-[340px] p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-[rgba(239,68,68,0.1)] rounded-full flex items-center justify-center mx-auto mb-4">
                <LogOut size={24} className="text-[#ef4444]" />
              </div>
              <p
                className="text-[18px] text-[#0d2b35] mb-2"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                Are you sure to logout?
              </p>
              <p
                className="text-[14px] text-[#637c84]"
                style={{
                  fontFamily: "'Nunito Sans', sans-serif",
                }}
              >
                You will need to login again to access your account.
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowLogoutModal(false)}
                disabled={isLoggingOut}
                className="flex-1 h-[48px] bg-[rgba(226,234,235,0.5)] text-[#0d2b35] rounded-2xl border-none cursor-pointer text-[16px] disabled:opacity-50"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  setIsLoggingOut(true);
                  await new Promise(resolve => setTimeout(resolve, 1500));
                  logout();
                  navigate("/login");
                }}
                disabled={isLoggingOut}
                className="flex-1 h-[48px] bg-[#ef4444] text-white rounded-2xl border-none cursor-pointer text-[16px] flex items-center justify-center gap-2 disabled:opacity-50"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                {isLoggingOut ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Logging out...
                  </>
                ) : (
                  "Logout"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </ResponsiveLayout>
  );
}
