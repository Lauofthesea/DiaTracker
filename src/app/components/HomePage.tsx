import { useNavigate } from "react-router";
import { useState, useEffect } from "react";
import ResponsiveLayout from "./ResponsiveLayout";
import { HealthCheckModal } from "./health-check";
import ProfileSetupModal from "./profile/ProfileSetupModal";
import { useAuth } from "../contexts/AuthContext";
import { getDailySummary } from "@/lib/foodApi";
import { getProfile, updateProfile } from "@/lib/profileApi";
import { getLatestHealthCheck } from "@/lib/healthCheck";
import type { DailyNutritionalSummary } from "@/types/food";
import type { ProfileResponse } from "@/types/profile";

export default function HomePage() {
  const navigate = useNavigate();
  const { user, refreshUserData } = useAuth();
  const [showProfileSetupModal, setShowProfileSetupModal] = useState(false);
  const [showHealthCheckModal, setShowHealthCheckModal] = useState(false);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [dailySummary, setDailySummary] = useState<DailyNutritionalSummary | null>(null);
  const [latestHealthCheck, setLatestHealthCheck] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Show appropriate modal on first login
    if (user?.isFirstLogin && profile) {
      // Check if profile is complete
      if (!profile.age || !profile.height_cm || !profile.gender) {
        setShowProfileSetupModal(true);
      } else {
        setShowHealthCheckModal(true);
      }
    }
  }, [user, profile]);

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
      const [profileData, summaryData, healthCheckData] = await Promise.all([
        getProfile().catch(() => null),
        getDailySummary(today).catch(() => null),
        getLatestHealthCheck().catch(() => null),
      ]);

      setProfile(profileData);
      setDailySummary(summaryData);
      setLatestHealthCheck(healthCheckData);
    } catch (err) {
      console.error('Error loading home page data:', err);
      setError('Failed to load data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSetupComplete = async (data: any) => {
    try {
      await updateProfile({
        age: data.age,
        height_cm: data.height_cm,
        gender: data.gender,
        is_pregnant: data.is_pregnant,
        allergen_preferences: data.allergens,
        health_conditions: data.health_conditions,
      });
      setShowProfileSetupModal(false);
      // Reload profile data
      const profileData = await getProfile();
      setProfile(profileData);
      // Now show health check modal
      setShowHealthCheckModal(true);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError('Failed to save profile. Please try again.');
    }
  };

  const handleHealthCheckComplete = async () => {
    setShowHealthCheckModal(false);
    await refreshUserData();
    loadData();
  };

  const calorieGoal = 2000;
  const caloriesConsumed = dailySummary?.total_calories || 0;
  const caloriesRemaining = Math.max(0, calorieGoal - caloriesConsumed);
  const calorieProgress = Math.min(100, (caloriesConsumed / calorieGoal) * 100);

  const carbGoal = 220;
  const carbsConsumed = dailySummary?.total_carbohydrates_g || 0;
  const carbProgress = Math.min(100, (carbsConsumed / carbGoal) * 100);
  const carbsNearingLimit = carbProgress >= 80;

  const currentGlucose = latestHealthCheck?.blood_sugar_mgdl || profile?.current_health_metrics?.blood_sugar_mgdl || 104;
  
  const trendColors = [
    '#10b981', '#10b981', '#84cc16', '#eab308', '#f59e0b', '#ef4444'
  ];
  
  const getCurrentBarIndex = (glucose: number) => {
    if (glucose < 80) return 0;
    if (glucose < 100) return 1;
    if (glucose < 120) return 2;
    if (glucose < 140) return 3;
    if (glucose < 160) return 4;
    return 5;
  };
  
  const currentBarIndex = getCurrentBarIndex(currentGlucose);
  const currentTrendColor = trendColors[currentBarIndex];
  
  const glucoseStatus = currentBarIndex <= 1 ? 'In Range' : 
                        currentBarIndex <= 3 ? 'Elevated' : 'High';
  const glucoseStatusColor = currentTrendColor;

  const carbImpact = dailySummary?.total_carbohydrates_g 
    ? Math.round((dailySummary.total_carbohydrates_g / 10) * 2)
    : 0;
  const predictedPeak = currentGlucose + Math.max(carbImpact, 20);
  const predictedBarIndex = getCurrentBarIndex(predictedPeak);
  
  const glucoseTrend = [
    { value: Math.max(70, currentGlucose - 30), height: 15, index: 0 },
    { value: Math.max(70, currentGlucose - 20), height: 20, index: 1 },
    { value: Math.max(70, currentGlucose - 10), height: 29, index: 2 },
    { value: currentGlucose - 5, height: 39, index: 3 },
    { value: currentGlucose, height: 41, index: 4 },
    { value: predictedPeak, height: Math.min(64, 41 + ((predictedPeak - currentGlucose) / 2)), index: 5 },
  ].map((point, idx) => ({
    ...point,
    baseColor: trendColors[idx],
    isActive: idx === currentBarIndex,
    isCurrent: idx === currentBarIndex,
  }));
  
  const hasCompletedHealthCheck = !!latestHealthCheck || !!profile?.current_health_metrics;
  const hasHealthConcern = predictedPeak > 140 || currentBarIndex > 1;
  const showAttentionNotice = hasCompletedHealthCheck && hasHealthConcern;

  const today = new Date();
  const formattedDate = today.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  const showDashboardData = !showProfileSetupModal && !showHealthCheckModal;

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

            <div className="px-6 pt-6 space-y-6">
              
              {showDashboardData && (
                <>
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
                        {dailySummary?.total_carbohydrates_g 
                          ? `Your predicted glucose peak of ${predictedPeak} mg/dL (from ${Math.round(dailySummary.total_carbohydrates_g)}g carbs) indicates elevated risk. Consider a 15-minute walk.`
                          : `Your glucose status indicates attention needed. Consider monitoring your levels and staying active.`}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="relative mb-4">
                <div className="absolute top-0 left-0 right-0 bg-gradient-to-br from-[#10b981]/10 via-[#3b82f6]/5 to-transparent -mx-6 rounded-3xl pointer-events-none" style={{ height: '240px' }} />
                
                <div className="relative flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full shadow-lg overflow-hidden ring-2 ring-white">
                      <div className="w-full h-full bg-gradient-to-br from-[#10b981] to-[#3b82f6] animate-pulse" />
                    </div>
                    <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                      Glucose Tracker
                    </h2>
                  </div>
                  <div 
                    className="px-4 py-1.5 rounded-full text-sm font-['Nunito_Sans'] font-bold shadow-md"
                    style={{ 
                      backgroundColor: glucoseStatusColor,
                      color: 'white'
                    }}
                  >
                    {glucoseStatus}
                  </div>
                </div>

                <div className="relative bg-gradient-to-br from-white to-[#f0fdf4] rounded-3xl p-6 mb-4 border-2 border-[#10b981]/20">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="font-['Nunito_Sans'] text-sm font-semibold mb-2 uppercase tracking-wide"
                         style={{ color: glucoseStatusColor }}
                      >
                        Current Estimate
                      </p>
                      <div className="flex items-baseline gap-2">
                        <span 
                          className="font-['Geist'] font-black text-6xl tracking-[-2.4px]"
                          style={{ color: glucoseStatusColor }}
                        >
                          {currentGlucose}
                        </span>
                        <span className="font-['Nunito_Sans'] text-lg font-bold mb-3"
                              style={{ color: glucoseStatusColor }}
                        >
                          mg/dL
                        </span>
                      </div>
                      <p className="font-['Nunito_Sans'] text-xs text-[#6b7280] mt-1">
                        Based on {dailySummary?.total_calories ? 'recent meals' : 'latest health check'}
                      </p>
                    </div>
                    
                    <div className="flex items-end gap-2 h-16">
                      {glucoseTrend.map((point, idx) => (
                        <div key={idx} className="relative flex flex-col justify-end" style={{ height: '64px' }}>
                          <div 
                            className="w-7 rounded-t-xl transition-all"
                            style={{ 
                              height: `${point.height * 1.2}px`,
                              backgroundColor: point.isActive ? point.baseColor : `${point.baseColor}40`, // 40 = 25% opacity for greyed out
                              opacity: point.isActive ? 1 : 0.4,
                            }}
                          >
                            {point.isCurrent && (
                              <div 
                                className="absolute -top-2 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full animate-pulse"
                                style={{ 
                                  backgroundColor: point.baseColor,
                                  boxShadow: `0px 0px 12px 0px ${point.baseColor}99`
                                }}
                              />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-[#fef3c7] to-[#fde68a] rounded-2xl p-5 border-2 border-[#fbbf24]/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white rounded-full shadow-md flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 20 20">
                          <path 
                            d="M10 3V17M10 3L6 7M10 3L14 7" 
                            stroke="#f59e0b" 
                            strokeWidth="2" 
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="font-['Nunito_Sans'] font-bold text-sm text-[#92400e]">
                          Predicted Peak
                        </p>
                        <p className="font-['Nunito_Sans'] text-xs text-[#b45309]">
                          {dailySummary?.total_carbohydrates_g 
                            ? `From ${Math.round(dailySummary.total_carbohydrates_g)}g carbs today`
                            : 'Based on typical response'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-['Geist'] font-black text-2xl text-[#92400e]">
                        {predictedPeak}
                      </p>
                      <div className="flex items-center gap-1 justify-end">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 16 16">
                          <path 
                            d="M8 12V4M8 4L4 8M8 4L12 8" 
                            stroke="#f59e0b" 
                            strokeWidth="1.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                          />
                        </svg>
                        <span className="font-['Nunito_Sans'] font-bold text-sm text-[#f59e0b]">
                          +{predictedPeak - currentGlucose}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                
                <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 bg-[#FEF3C7] rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4" fill="#F59E0B" viewBox="0 0 20 20">
                        <path d="M10 2C10 2 8 4 8 6C8 7.1 8.9 8 10 8C11.1 8 12 7.1 12 6C12 4 10 2 10 2ZM10 9C8.34 9 7 10.34 7 12C7 13.66 8.34 15 10 15C11.66 15 13 13.66 13 12C13 10.34 11.66 9 10 9ZM10 16C7.79 16 6 17.79 6 20H14C14 17.79 12.21 16 10 16Z" />
                      </svg>
                    </div>
                    <span className="font-['Geist'] font-medium text-sm text-[#637c84]">
                      Calories
                    </span>
                  </div>
                  
                  {}
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

                <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-[0px_4px_24px_0px_rgba(13,43,53,0.06)] p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 bg-[#FEF9C3] rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4" fill="#EAB308" viewBox="0 0 20 20">
                        <path d="M3 4C3 2.89543 3.89543 2 5 2H15C16.1046 2 17 2.89543 17 4V16C17 17.1046 16.1046 18 15 18H5C3.89543 18 3 17.1046 3 16V4ZM5 4H15V16H5V4ZM7 7H13V9H7V7ZM7 11H13V13H7V11Z" />
                      </svg>
                    </div>
                    <span className="font-['Geist'] font-medium text-sm text-[#637c84]">
                      Carbs
                    </span>
                  </div>
                  
                  {}
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

              <button
                onClick={() => navigate("/log-meal")}
                className="w-full bg-[#1e6177] text-white rounded-full py-4 shadow-[0px_4px_6px_0px_rgba(30,97,119,0.25),0px_10px_15px_0px_rgba(30,97,119,0.25)] font-['Geist'] font-medium text-lg flex items-center justify-center gap-2 hover:bg-[#1a5566] transition-colors"
              >
                <svg className="w-6 h-6" fill="white" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 5a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H6a1 1 0 110-2h5V6a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Log New Meal
              </button>
              </>
            )}

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
        
        {showProfileSetupModal && (
          <ProfileSetupModal onComplete={handleProfileSetupComplete} />
        )}
        
        <HealthCheckModal
          open={showHealthCheckModal}
          onComplete={handleHealthCheckComplete}
          profileData={{
            age: profile?.age || null,
            height_cm: profile?.height_cm || null
          }}
        />
      </div>
    </ResponsiveLayout>
  );
}
