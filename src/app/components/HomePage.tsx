import { useNavigate } from "react-router";
import { useState, useEffect } from "react";
import ResponsiveLayout from "./ResponsiveLayout";
import { HealthCheckModal } from "./health-check";
import { useAuth } from "../contexts/AuthContext";
import { getDailySummary } from "@/lib/foodApi";
import { getProfile } from "@/lib/profileApi";
import { getLatestHealthCheck } from "@/lib/healthCheck";
import type { DailyNutritionalSummary } from "@/types/food";
import type { ProfileResponse } from "@/types/profile";

export default function HomePage() {
  const navigate = useNavigate();
  const { user, refreshUserData } = useAuth();
  const [showHealthCheckModal, setShowHealthCheckModal] = useState(false);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [dailySummary, setDailySummary] = useState<DailyNutritionalSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Show health check modal on first login
    if (user?.isFirstLogin) {
      setShowHealthCheckModal(true);
    }
  }, [user]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get today's date in YYYY-MM-DD format
      const today = new Date().toISOString().split('T')[0];

      // Fetch all data in parallel
      const [profileData, summaryData] = await Promise.all([
        getProfile().catch(() => null),
        getDailySummary(today).catch(() => null),
        getLatestHealthCheck().catch(() => null), // For future use
      ]);

      setProfile(profileData);
      setDailySummary(summaryData);
    } catch (err) {
      console.error('Error loading home page data:', err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleHealthCheckComplete = async () => {
    setShowHealthCheckModal(false);
    // Refresh user data to update first_login_completed status
    await refreshUserData();
    // Reload data to get updated prediction
    loadData();
  };

  // Calculate calorie progress
  const calorieGoal = 2000;
  const caloriesConsumed = dailySummary?.total_calories || 0;
  const caloriesRemaining = Math.max(0, calorieGoal - caloriesConsumed);
  const calorieProgress = Math.min(100, (caloriesConsumed / calorieGoal) * 100);

  // Calculate carb progress
  const carbGoal = 220;
  const carbsConsumed = dailySummary?.total_carbohydrates_g || 0;
  const carbProgress = Math.min(100, (carbsConsumed / carbGoal) * 100);
  const carbsNearingLimit = carbProgress >= 80;

  // Get current glucose estimate from latest prediction
  const currentGlucose = profile?.current_health_metrics?.blood_sugar_mgdl || 104;
  const glucoseStatus = currentGlucose >= 70 && currentGlucose <= 140 ? 'In Range' : 
                        currentGlucose < 70 ? 'Low' : 'High';
  const glucoseStatusColor = glucoseStatus === 'In Range' ? '#179b6b' : 
                             glucoseStatus === 'Low' ? '#f59e0b' : '#dc2626';

  // Predicted peak glucose (mock calculation - would come from ML model)
  const predictedPeak = currentGlucose + 38;
  const showAttentionNotice = predictedPeak > 140;

  // Format today's date
  const today = new Date();
  const formattedDate = today.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  // Mock glucose trend data (would come from API)
  const glucoseTrend = [
    { value: 95, height: 15 },
    { value: 98, height: 20 },
    { value: 102, height: 29 },
    { value: 108, height: 39 },
    { value: currentGlucose, height: 41 },
    { value: 115, height: 46 },
  ];

  if (loading) {
    return (
      <ResponsiveLayout>
        <div className="bg-[#f4f8f8] min-h-screen w-full flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#1e6177] mx-auto mb-4"></div>
            <p className="text-[#637c84] font-['Nunito_Sans']">Loading your dashboard...</p>
          </div>
        </div>
      </ResponsiveLayout>
    );
  }

  return (
    <ResponsiveLayout>
      <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto relative">
        <div className="relative overflow-auto" style={{ minHeight: "100dvh" }}>
          <div className="relative max-w-[430px] mx-auto md:max-w-full md:px-8 lg:px-12 pb-24">
            
            {/* Header */}
            <header className="backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-[rgba(226,234,235,0.4)] border-b-[0.8px] border-solid px-6 py-4 sticky top-0 z-10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full shadow-[0px_1px_2px_-1px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1),0px_0px_0px_2px_rgba(30,97,119,0.1)] bg-gradient-to-br from-[#1e6177] to-[#8aab9f]"
                  />
                  <div>
                    <p className="font-['Nunito_Sans'] text-sm text-[#637c84]">
                      Date Today: {formattedDate}
                    </p>
                    <h1 className="font-['Geist'] font-semibold text-lg text-[#0d2b35] tracking-[-0.45px]">
                      Hello, {profile?.name || user?.name || 'User'}!
                    </h1>
                  </div>
                </div>
                <button 
                  className="w-10 h-10 rounded-full bg-[rgba(214,230,225,0.5)] flex items-center justify-center relative"
                  onClick={() => navigate('/health-check')}
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24">
                    <path 
                      d="M12 2v20M2 12h20" 
                      stroke="#204A3A" 
                      strokeWidth="1.5" 
                      strokeLinecap="round"
                    />
                  </svg>
                  {showAttentionNotice && (
                    <div className="absolute top-2.5 right-2.5 w-2 h-2 bg-[#d97706] border-2 border-[#f4f8f8] rounded-full" />
                  )}
                </button>
              </div>
            </header>

            {/* Main Content */}
            <div className="px-6 pt-6 space-y-6">
              
              {/* Attention Notice */}
              {showAttentionNotice && (
                <div className="bg-[rgba(254,243,199,0.4)] border-[0.8px] border-[rgba(254,243,199,0.2)] rounded-2xl p-4 relative overflow-hidden">
                  <div className="absolute -top-10 -right-10 w-40 h-40 bg-[rgba(245,158,11,0.1)] rounded-full blur-[32px]" />
                  <div className="relative flex gap-3">
                    <div className="w-10 h-10 bg-[#fef3c7] rounded-full shadow-sm flex items-center justify-center flex-shrink-0">
                      <svg className="w-5 h-5" fill="#92400e" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-['Geist'] font-semibold text-[#92400e] text-base mb-1">
                        Attention Needed
                      </h3>
                      <p className="font-['Nunito_Sans'] text-sm text-[rgba(146,64,14,0.8)] leading-relaxed">
                        Your predicted glucose indicates a moderate risk of hyperglycemia following your last logged meal. Consider a 15-minute walk.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Glucose Status Gradient Background */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-b from-[rgba(138,171,159,0.05)] to-transparent h-64 -mx-6" />
                
                {/* Glucose Status Header */}
                <div className="relative flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full shadow-sm overflow-hidden">
                      <div className="w-full h-full bg-gradient-to-br from-[#1e6177] to-[#8aab9f]" />
                    </div>
                    <h2 className="font-['Geist'] font-semibold text-lg text-[#0d2b35] tracking-[-0.45px]">
                      Glucose Status
                    </h2>
                  </div>
                  <div 
                    className="px-3 py-1 rounded-full text-xs font-['Nunito_Sans'] font-semibold"
                    style={{ 
                      backgroundColor: `${glucoseStatusColor}1A`,
                      color: glucoseStatusColor 
                    }}
                  >
                    {glucoseStatus}
                  </div>
                </div>

                {/* Current Glucose Estimate */}
                <div className="relative bg-white/50 backdrop-blur-sm rounded-2xl p-6 mb-4">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="font-['Nunito_Sans'] text-sm text-[#637c84] mb-1">
                        Current Estimate
                      </p>
                      <div className="flex items-baseline gap-2">
                        <span className="font-['Geist'] font-bold text-5xl text-[#0d2b35] tracking-[-2.4px]">
                          {currentGlucose}
                        </span>
                        <span className="font-['Nunito_Sans'] text-base text-[#637c84] mb-2">
                          mg/dL
                        </span>
                      </div>
                    </div>
                    
                    {/* Mini Glucose Trend Chart */}
                    <div className="flex items-end gap-2 h-12">
                      {glucoseTrend.map((point, idx) => (
                        <div key={idx} className="relative flex flex-col justify-end" style={{ height: '48px' }}>
                          <div 
                            className="w-6 rounded-t-xl transition-all"
                            style={{ 
                              height: `${point.height}px`,
                              backgroundColor: idx === glucoseTrend.length - 2 
                                ? 'rgba(138,171,159,0.6)' 
                                : idx === glucoseTrend.length - 1
                                ? 'rgba(254,243,199,0.4)'
                                : 'rgba(226,234,235,0.5)'
                            }}
                          >
                            {idx === glucoseTrend.length - 2 && (
                              <div className="absolute -top-1.5 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-[#8aab9f] rounded-full shadow-[0px_0px_8px_0px_rgba(138,171,159,0.8)]" />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Predicted Peak */}
                <div className="bg-[rgba(214,230,225,0.4)] rounded-2xl p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-[#f4f8f8] rounded-full shadow-sm flex items-center justify-center">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                          <path 
                            d="M8 2v12M14 8H2" 
                            stroke="#0D2B35" 
                            strokeWidth="1" 
                            strokeLinecap="round"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="font-['Nunito_Sans'] font-medium text-sm text-[#0d2b35]">
                          Predicted Peak
                        </p>
                        <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                          Based on latest meal
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-['Geist'] font-semibold text-lg text-[#0d2b35]">
                        {predictedPeak}
                      </p>
                      <div className="flex items-center gap-1 justify-end">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 12 12">
                          <path 
                            d="M3 9L9 3M9 3H4.5M9 3V7.5" 
                            stroke="#F59E0B" 
                            strokeWidth="0.75" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          />
                        </svg>
                        <span className="font-['Nunito_Sans'] font-medium text-xs text-[#f59e0b]">
                          +{predictedPeak - currentGlucose} higher
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Calorie and Carb Tracking */}
              <div className="grid grid-cols-2 gap-4">
                
                {/* Calorie Card */}
                <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <svg className="w-4 h-4" fill="#F59E0B" viewBox="0 0 16 16">
                      <path fillRule="evenodd" d="M8.5 1.5a.5.5 0 00-1 0v1.293l-1.146-1.147a.5.5 0 00-.708.708L7.293 4H6a.5.5 0 000 1h2a.5.5 0 00.5-.5v-2a.5.5 0 00-.5-.5zm-3 9a.5.5 0 01.5.5v2a.5.5 0 01-.5.5H4a.5.5 0 010-1h1v-1.5a.5.5 0 01.5-.5z" clipRule="evenodd" />
                    </svg>
                    <span className="font-['Geist'] font-medium text-sm text-[#637c84]">
                      Calories
                    </span>
                  </div>
                  
                  {/* Circular Progress */}
                  <div className="relative w-24 h-24 mx-auto mb-4">
                    <svg className="w-full h-full -rotate-90">
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="42.67" 
                        fill="none" 
                        stroke="#E2EAEB" 
                        strokeWidth="10.67"
                      />
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="42.67" 
                        fill="none" 
                        stroke="#3ADE3F" 
                        strokeWidth="10.67"
                        strokeDasharray={`${calorieProgress * 2.68} 268`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="font-['Geist'] font-bold text-lg text-[#0d2b35] tracking-[-0.45px]">
                        {Math.round(caloriesConsumed)}
                      </span>
                      <span className="font-['Nunito_Sans'] font-semibold text-[10px] text-[#637c84] uppercase tracking-wider">
                        / {calorieGoal}
                      </span>
                    </div>
                  </div>
                  
                  <p className="font-['Nunito_Sans'] font-medium text-sm text-[#1e6177] text-center">
                    {caloriesRemaining} remaining
                  </p>
                </div>

                {/* Carb Card */}
                <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <svg className="w-4 h-4" fill="#FCD34D" viewBox="0 0 16 16">
                      <path fillRule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z" clipRule="evenodd" />
                    </svg>
                    <span className="font-['Geist'] font-medium text-sm text-[#637c84]">
                      Carbs
                    </span>
                  </div>
                  
                  {/* Circular Progress */}
                  <div className="relative w-24 h-24 mx-auto mb-4">
                    <svg className="w-full h-full -rotate-90">
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="42.67" 
                        fill="none" 
                        stroke="#E2EAEB" 
                        strokeWidth="10.67"
                      />
                      <circle 
                        cx="48" 
                        cy="48" 
                        r="42.67" 
                        fill="none" 
                        stroke="#FFEE57" 
                        strokeWidth="10.67"
                        strokeDasharray={`${carbProgress * 2.68} 268`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="font-['Geist'] font-bold text-lg text-[#0d2b35] tracking-[-0.45px]">
                        {Math.round(carbsConsumed)}g
                      </span>
                      <span className="font-['Nunito_Sans'] font-semibold text-[10px] text-[#637c84] uppercase tracking-wider">
                        / {carbGoal}g
                      </span>
                    </div>
                  </div>
                  
                  <p className={`font-['Nunito_Sans'] font-medium text-sm text-center ${
                    carbsNearingLimit ? 'text-[#f59e0b]' : 'text-[#1e6177]'
                  }`}>
                    {carbsNearingLimit ? 'Nearing limit' : `${carbGoal - Math.round(carbsConsumed)}g remaining`}
                  </p>
                </div>
              </div>

              {/* Log New Meal Button */}
              <button
                onClick={() => navigate("/log-meal")}
                className="w-full bg-[#1e6177] text-white rounded-full py-4 shadow-[0px_4px_6px_0px_rgba(30,97,119,0.25),0px_10px_15px_0px_rgba(30,97,119,0.25)] font-['Geist'] font-medium text-lg flex items-center justify-center gap-2 hover:bg-[#1a5566] transition-colors"
              >
                <svg className="w-6 h-6" fill="white" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 5a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H6a1 1 0 110-2h5V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Log New Meal
              </button>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                  <p className="text-red-600 text-sm">{error}</p>
                  <button 
                    onClick={loadData}
                    className="mt-2 text-red-700 underline text-sm"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Health Check Modal for first-time users */}
        <HealthCheckModal
          open={showHealthCheckModal}
          onComplete={handleHealthCheckComplete}
        />
      </div>
    </ResponsiveLayout>
  );
}
