import { useNavigate } from "react-router";
import { useState, useEffect } from "react";
import ResponsiveLayout from "./ResponsiveLayout";
import { HealthCheckModal } from "./health-check";
import ProfileSetupModal from "./profile/ProfileSetupModal";
import { useAuth } from "../contexts/AuthContext";
import { getDailySummary, getFoodEntries } from "@/lib/foodApi";
import { getProfile, updateProfile, getHealthMetricsHistory } from "@/lib/profileApi";
import { getLatestHealthCheck } from "@/lib/healthCheck";
import { getTodaysMealPredictions, getMealHistory, type MealPrediction } from "@/lib/mealRiskApi";
import { calculateCurrentGlucose, getTimeSinceMealDescription, isMealPredictionRelevant } from "@/lib/glucoseDynamics";
import type { DailyNutritionalSummary, FoodEntry } from "@/types/food";
import type { ProfileResponse, HealthMetricsHistoryItem } from "@/types/profile";

export default function HomePage() {
  const navigate = useNavigate();
  const { user, refreshUserData } = useAuth();
  const [showProfileSetupModal, setShowProfileSetupModal] = useState(false);
  const [showHealthCheckModal, setShowHealthCheckModal] = useState(false);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [dailySummary, setDailySummary] = useState<DailyNutritionalSummary | null>(null);
  const [latestHealthCheck, setLatestHealthCheck] = useState<any>(null);
  const [riskHistory, setRiskHistory] = useState<HealthMetricsHistoryItem[]>([]);
  const [todaysMealPredictions, setTodaysMealPredictions] = useState<MealPrediction[]>([]);
  const [weekMealPredictions, setWeekMealPredictions] = useState<MealPrediction[]>([]);
  const [weekFoodEntries, setWeekFoodEntries] = useState<FoodEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.isFirstLogin && profile) {
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

      // Get today's date in local timezone (YYYY-MM-DD format)
      const today = new Date();
      const localDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

      // Get date 7 days ago for meal history
      const sevenDaysAgo = new Date(today);
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      const startDate = sevenDaysAgo.toISOString();
      const endDate = today.toISOString();

      const [profileData, summaryData, healthCheckData, historyData, mealPredictions, weekMeals, foodEntries] = await Promise.all([
        getProfile().catch(() => null),
        getDailySummary(localDate).catch(() => null),
        getLatestHealthCheck().catch(() => null),
        getHealthMetricsHistory(1, 7).catch(() => ({ metrics: [] })),
        getTodaysMealPredictions().catch(() => []),
        getMealHistory(startDate, endDate, undefined, 1, 100).catch(() => ({ predictions: [], pagination: { page: 1, page_size: 100, total_count: 0, total_pages: 0 } })),
        getFoodEntries({ start_date: startDate, end_date: endDate, page: 1, page_size: 100 }).catch(() => ({ entries: [], total: 0, page: 1, page_size: 100, total_pages: 0 })),
      ]);

      setProfile(profileData);
      setDailySummary(summaryData);
      setLatestHealthCheck(healthCheckData);
      setRiskHistory(historyData.metrics || []);
      setTodaysMealPredictions(mealPredictions);
      setWeekMealPredictions(weekMeals.predictions || []);
      setWeekFoodEntries(foodEntries.entries || []);
    } catch (err) {
      console.error('Error loading home page data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSetupComplete = async (data: any) => {
    try {
      await updateProfile({
        age: data.age,
        weight_kg: data.weight_kg,
        height_cm: data.height_cm,
        gender: data.gender,
        is_pregnant: data.is_pregnant,
        family_history: data.has_family_history,
      });
      setShowProfileSetupModal(false);
      const profileData = await getProfile();
      setProfile(profileData);
      setShowHealthCheckModal(true);
    } catch (err) {
      console.error('Failed to update profile:', err);
    }
  };

  const handleHealthCheckComplete = async () => {
    setShowHealthCheckModal(false);
    await refreshUserData();
    loadData();
  };

  // Calculate current glucose and status with clinical adjustments
  // Baseline glucose from latest health check
  const baselineGlucose = latestHealthCheck?.blood_sugar_mgdl || 
                          profile?.current_health_metrics?.blood_sugar_mgdl || 
                          null;
  
  // Get relevant meal predictions (within last 5 hours - clinical evidence shows glucose returns to baseline by then)
  const currentTime = new Date();
  const relevantMealPredictions = todaysMealPredictions.filter(pred => 
    isMealPredictionRelevant(new Date(pred.predicted_at), currentTime)
  );
  
  // Find most recent meal prediction
  const mostRecentPrediction = relevantMealPredictions.length > 0
    ? relevantMealPredictions.reduce((latest, current) => {
        const latestTime = new Date(latest.predicted_at).getTime();
        const currentTime = new Date(current.predicted_at).getTime();
        return currentTime > latestTime ? current : latest;
      })
    : null;
  
  // Calculate current glucose with clinical adjustments
  let currentGlucose: number | null = null;
  let glucoseExplanation = '';
  
  if (mostRecentPrediction && profile && baselineGlucose && profile.height_cm && profile.weight_kg && profile.age) {
    // Calculate BMI
    const heightM = profile.height_cm / 100;
    const bmi = profile.weight_kg / (heightM * heightM);
    
    // Apply clinical glucose dynamics
    const glucoseEstimate = calculateCurrentGlucose({
      predictedGlucose1hr: mostRecentPrediction.predicted_glucose_1hr,
      baselineGlucose: baselineGlucose,
      mealTime: new Date(mostRecentPrediction.predicted_at),
      currentTime: currentTime,
      age: profile.age || 30,
      gender: (profile.gender?.toLowerCase() as 'male' | 'female') || 'male',
      bmi: bmi,
      mealType: undefined // We don't have meal type in prediction, will use time-of-day
    });
    
    currentGlucose = glucoseEstimate.currentGlucose;
    const timeSince = getTimeSinceMealDescription(glucoseEstimate.hoursSinceMeal);
    glucoseExplanation = `${glucoseEstimate.explanation} (meal ${timeSince})`;
  } else if (baselineGlucose) {
    // No recent meals, show baseline
    currentGlucose = baselineGlucose;
    glucoseExplanation = 'Based on latest health check';
  }
  
  // Helper functions for status
  const getFastingStatus = (g: number) => {
    if (g < 100) return { 
      label: 'Low Risk', 
      status: 'In Range', 
      color: '#10b981', 
      bgColor: 'rgba(16,185,129,0.08)', 
      borderColor: 'rgba(16,185,129,0.25)', 
      advice: 'Fasting glucose is within the healthy range.' 
    };
    if (g < 126) return { 
      label: 'Mid Risk', 
      status: 'Elevated', 
      color: '#f59e0b', 
      bgColor: 'rgba(245,158,11,0.08)', 
      borderColor: 'rgba(245,158,11,0.25)', 
      advice: 'Fasting glucose is above normal. Consider scheduling a check-up.' 
    };
    return { 
      label: 'High Risk', 
      status: 'High', 
      color: '#ef4444', 
      bgColor: 'rgba(239,68,68,0.08)', 
      borderColor: 'rgba(239,68,68,0.25)', 
      advice: 'Fasting glucose is critically high. Please consult a doctor soon.' 
    };
  };

  const getPostMealStatus = (g: number) => {
    if (g < 140) return { 
      label: 'Low Risk', 
      status: 'In Range', 
      color: '#10b981', 
      bgColor: 'rgba(16,185,129,0.08)', 
      borderColor: 'rgba(16,185,129,0.25)', 
      advice: 'Your body handled this meal well.' 
    };
    if (g < 200) return { 
      label: 'Mid Risk', 
      status: 'Elevated', 
      color: '#f59e0b', 
      bgColor: 'rgba(245,158,11,0.08)', 
      borderColor: 'rgba(245,158,11,0.25)', 
      advice: 'Mild post-meal rise. Try smaller portions or lower-GI foods next time.' 
    };
    return { 
      label: 'High Risk', 
      status: 'High', 
      color: '#ef4444', 
      bgColor: 'rgba(239,68,68,0.08)', 
      borderColor: 'rgba(239,68,68,0.25)', 
      advice: 'Significant post-meal spike. Consider reducing carbs in this meal type.' 
    };
  };

  // Determine if current glucose is post-meal or fasting
  const isPostMeal = mostRecentPrediction !== null;

  // Get current risk level
  const currentRisk = latestHealthCheck?.classification || 'Unknown';
  const getRiskColor = (risk: string) => {
    if (risk === 'Low') return { color: '#10b981', bgColor: 'rgba(16,185,129,0.1)' };
    if (risk === 'Mid') return { color: '#f59e0b', bgColor: 'rgba(245,158,11,0.1)' };
    if (risk === 'High') return { color: '#ef4444', bgColor: 'rgba(239,68,68,0.1)' };
    return { color: '#637c84', bgColor: 'rgba(99,124,132,0.1)' };
  };

  const riskColor = getRiskColor(currentRisk);

  // Calculate days since last check
  const getDaysSinceLastCheck = () => {
    if (!latestHealthCheck?.predicted_at) return null;
    const lastCheck = new Date(latestHealthCheck.predicted_at);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - lastCheck.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysSinceLastCheck = getDaysSinceLastCheck();

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
            
            {/* Header */}
            <header className="backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-[rgba(226,234,235,0.4)] border-b-[0.8px] border-solid px-6 py-4 sticky top-0 z-10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-full shadow-[0px_1px_2px_-1px_rgba(0,0,0,0.1),0px_1px_3px_0px_rgba(0,0,0,0.1),0px_0px_0px_2px_rgba(30,97,119,0.1)] bg-gradient-to-br from-[#1e6177] to-[#8aab9f]"
                  />
                  <div>
                    <h1 className="font-['Geist'] font-semibold text-lg text-[#0d2b35] tracking-[-0.45px]">
                      Hello, {profile?.name || user?.name || 'User'}!
                    </h1>
                    <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                      {formattedDate}
                    </p>
                  </div>
                </div>
              </div>
            </header>

            <div className="px-6 pt-4 space-y-4">
              
              {showDashboardData && (
                <>
                  {/* Card 1: Fasting Baseline - Always Visible */}
                  {baselineGlucose && (() => {
                    const st = getFastingStatus(baselineGlucose);
                    return (
                      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                              Fasting Baseline
                            </h2>
                            <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                              From latest health check
                            </p>
                          </div>
                          <span className="px-3 py-1.5 rounded-xl text-[12px] font-bold" style={{ backgroundColor: st.bgColor, color: st.color, border: `1px solid ${st.borderColor}` }}>
                            {st.label}
                          </span>
                        </div>
                        
                        <div className="rounded-2xl p-5" style={{ backgroundColor: st.bgColor, border: `1.5px solid ${st.borderColor}` }}>
                          <div className="flex items-baseline gap-1.5 mb-2">
                            <span className="font-['Geist'] font-black text-[52px] tracking-[-2px]" style={{ color: st.color }}>
                              {Math.round(baselineGlucose)}
                            </span>
                            <span className="font-['Nunito_Sans'] text-[15px] font-semibold mb-2" style={{ color: st.color }}>
                              mg/dL
                            </span>
                          </div>
                          <p className="font-['Nunito_Sans'] text-[13px] text-[#4b6068] mb-3 leading-relaxed">
                            {st.advice}
                          </p>
                          <div className="pt-2 flex items-center gap-1.5" style={{ borderTop: `1px solid ${st.borderColor}` }}>
                            <p className="font-['Nunito_Sans'] text-[11px]" style={{ color: st.color, opacity: 0.8 }}>
                              ADA: Normal &lt;100 · Pre-diabetic 100–125 · Diabetic ≥126
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Card 2: Post-meal Estimate - Only Visible When Recent Meal Exists */}
                  {isPostMeal && currentGlucose && (() => {
                    const st = getPostMealStatus(currentGlucose);
                    const delta = baselineGlucose ? currentGlucose - baselineGlucose : null;
                    const deltaColor = !delta ? '#637c84' : delta < 30 ? '#10b981' : delta < 60 ? '#f59e0b' : '#ef4444';
                    const deltaLabel = !delta ? '' : delta < 30 ? 'Minimal rise' : delta < 60 ? 'Moderate rise' : 'Large rise';
                    const showConflict = st.status === 'In Range' && baselineGlucose && getFastingStatus(baselineGlucose).status !== 'In Range';
                    
                    return (
                      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                              Post-meal Estimate
                            </h2>
                            <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                              {glucoseExplanation}
                            </p>
                          </div>
                          <span className="px-3 py-1.5 rounded-xl text-[12px] font-bold" style={{ backgroundColor: st.bgColor, color: st.color, border: `1px solid ${st.borderColor}` }}>
                            {st.label}
                          </span>
                        </div>
                        
                        <div className="rounded-2xl p-5 mb-3" style={{ backgroundColor: st.bgColor, border: `1.5px solid ${st.borderColor}` }}>
                          <div className="flex items-baseline justify-between mb-2">
                            <div className="flex items-baseline gap-1.5">
                              <span className="font-['Geist'] font-black text-[52px] tracking-[-2px]" style={{ color: st.color }}>
                                {Math.round(currentGlucose)}
                              </span>
                              <span className="font-['Nunito_Sans'] text-[15px] font-semibold mb-2" style={{ color: st.color }}>
                                mg/dL
                              </span>
                            </div>
                            {delta !== null && (
                              <div className="text-right">
                                <p className="font-['Geist'] font-black text-[22px] tracking-[-1px]" style={{ color: deltaColor }}>
                                  +{Math.round(delta)}
                                </p>
                                <p className="font-['Nunito_Sans'] text-[11px] font-semibold" style={{ color: deltaColor }}>
                                  {deltaLabel}
                                </p>
                              </div>
                            )}
                          </div>
                          <p className="font-['Nunito_Sans'] text-[13px] text-[#4b6068] mb-3 leading-relaxed">
                            {st.advice}
                          </p>
                          <div className="pt-2 flex items-center gap-1.5" style={{ borderTop: `1px solid ${st.borderColor}` }}>
                            <p className="font-['Nunito_Sans'] text-[11px]" style={{ color: st.color, opacity: 0.8 }}>
                              ADA: Good &lt;140 · Moderate 140–199 · High ≥200
                            </p>
                          </div>
                        </div>
                        
                        {showConflict && (
                          <div className="rounded-xl px-4 py-3 flex items-start gap-2.5" style={{ backgroundColor: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)' }}>
                            <span className="text-[#f59e0b] mt-0.5 flex-shrink-0">⚠️</span>
                            <p className="font-['Nunito_Sans'] text-[12px] text-[#92650a] leading-relaxed">
                              <strong>Good meal choice!</strong> Your post-meal response was healthy, but your fasting baseline is still {getFastingStatus(baselineGlucose!).label.toLowerCase()}. Keep eating well and consult your doctor about your baseline.
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  {/* Latest Health Assessment */}
                  <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                          Latest Health Assessment
                        </h2>
                        <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                          {daysSinceLastCheck !== null && (
                            daysSinceLastCheck === 0 ? 'Assessed today' : `${daysSinceLastCheck} day${daysSinceLastCheck > 1 ? 's' : ''} ago`
                          )}
                        </p>
                      </div>
                      <span className="px-3 py-1.5 rounded-xl text-[12px] font-bold" style={{ backgroundColor: riskColor.bgColor, color: riskColor.color, border: `1px solid ${riskColor.color}40` }}>
                        {currentRisk} Risk
                      </span>
                    </div>
                    
                    <div className="rounded-2xl p-5" style={{ backgroundColor: riskColor.bgColor, border: `1.5px solid ${riskColor.color}40` }}>
                      {/* Glucose Level from Assessment */}
                      {baselineGlucose && (
                        <div className="mb-4">
                          <p className="font-['Nunito_Sans'] text-[11px] text-[#637c84] uppercase tracking-[0.5px] mb-1 font-semibold">
                            Fasting Glucose
                          </p>
                          <div className="flex items-baseline gap-1.5">
                            <span className="font-['Geist'] font-black text-[42px] tracking-[-2px]" style={{ color: riskColor.color }}>
                              {baselineGlucose.toFixed(0)}
                            </span>
                            <span className="font-['Nunito_Sans'] text-[14px] font-semibold mb-2" style={{ color: riskColor.color }}>
                              mg/dL
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {/* Assessment Details */}
                      <div className="space-y-2 pt-3" style={{ borderTop: `1px solid ${riskColor.color}40` }}>
                        {profile?.age && (
                          <div className="flex justify-between items-center">
                            <span className="font-['Nunito_Sans'] text-[12px] text-[#637c84]">Age</span>
                            <span className="font-['Geist'] text-[12px] text-[#0d2b35] font-semibold">{profile.age} years</span>
                          </div>
                        )}
                        {profile?.weight_kg && profile?.height_cm && (
                          <div className="flex justify-between items-center">
                            <span className="font-['Nunito_Sans'] text-[12px] text-[#637c84]">BMI</span>
                            <span className="font-['Geist'] text-[12px] text-[#0d2b35] font-semibold">
                              {((profile.weight_kg / ((profile.height_cm / 100) ** 2))).toFixed(1)}
                            </span>
                          </div>
                        )}
                        {profile?.family_history !== null && profile?.family_history !== undefined && (
                          <div className="flex justify-between items-center">
                            <span className="font-['Nunito_Sans'] text-[12px] text-[#637c84]">Family History</span>
                            <span className="font-['Geist'] text-[12px] text-[#0d2b35] font-semibold">
                              {profile.family_history ? 'Yes' : 'No'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Meal History (Last 7 Days) */}
                  {weekMealPredictions.length > 0 && (
                    <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6">
                      <div className="mb-4">
                        <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                          Meal History
                        </h2>
                        <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                          Last 7 days
                        </p>
                      </div>
                      
                      {/* Column Headers */}
                      <div className="flex items-center gap-3 pb-2 mb-3 border-b-2 border-[rgba(226,234,235,0.5)]">
                        <div className="w-14 flex-shrink-0">
                          <span className="text-[10px] font-bold text-[#637c84] uppercase tracking-[0.5px]" style={{ fontFamily: "'Geist', sans-serif" }}>
                            Date
                          </span>
                        </div>
                        <div className="w-20 flex-shrink-0">
                          <span className="text-[10px] font-bold text-[#637c84] uppercase tracking-[0.5px]" style={{ fontFamily: "'Geist', sans-serif" }}>
                            Meal
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <span className="text-[10px] font-bold text-[#637c84] uppercase tracking-[0.5px]" style={{ fontFamily: "'Geist', sans-serif" }}>
                            Foods
                          </span>
                        </div>
                        <div className="w-16 flex-shrink-0 text-right">
                          <span className="text-[10px] font-bold text-[#637c84] uppercase tracking-[0.5px]" style={{ fontFamily: "'Geist', sans-serif" }}>
                            Glucose
                          </span>
                        </div>
                        <div className="w-14 flex-shrink-0 text-center">
                          <span className="text-[10px] font-bold text-[#637c84] uppercase tracking-[0.5px]" style={{ fontFamily: "'Geist', sans-serif" }}>
                            Risk
                          </span>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        {(() => {
                          // Group meals by day
                          const mealsByDay: { [key: string]: MealPrediction[] } = {};
                          
                          weekMealPredictions.forEach((meal) => {
                            const mealDate = new Date(meal.predicted_at);
                            const dateKey = `${mealDate.getFullYear()}-${String(mealDate.getMonth() + 1).padStart(2, '0')}-${String(mealDate.getDate()).padStart(2, '0')}`;
                            
                            if (!mealsByDay[dateKey]) {
                              mealsByDay[dateKey] = [];
                            }
                            mealsByDay[dateKey].push(meal);
                          });
                          
                          // Sort days in descending order (most recent first)
                          const sortedDays = Object.keys(mealsByDay).sort((a, b) => b.localeCompare(a));
                          
                          // Take only last 7 days
                          const last7Days = sortedDays.slice(0, 7);
                          
                          return last7Days.map((dateKey) => {
                            const meals = mealsByDay[dateKey];
                            const date = new Date(dateKey);
                            const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                            
                            // Categorize meals by time of day
                            const breakfast = meals.filter(m => {
                              const hour = new Date(m.predicted_at).getHours();
                              return hour >= 5 && hour < 11;
                            });
                            const lunch = meals.filter(m => {
                              const hour = new Date(m.predicted_at).getHours();
                              return hour >= 11 && hour < 16;
                            });
                            const dinner = meals.filter(m => {
                              const hour = new Date(m.predicted_at).getHours();
                              return hour >= 16 && hour < 24;
                            });
                            
                            // Get food entries for this day
                            const dayFoodEntries = weekFoodEntries.filter(entry => {
                              const entryDate = new Date(entry.consumed_at);
                              const entryDateKey = `${entryDate.getFullYear()}-${String(entryDate.getMonth() + 1).padStart(2, '0')}-${String(entryDate.getDate()).padStart(2, '0')}`;
                              return entryDateKey === dateKey;
                            });
                            
                            // Group food entries by meal type
                            const breakfastEntries = dayFoodEntries.filter(e => e.meal_type === 'breakfast');
                            const lunchEntries = dayFoodEntries.filter(e => e.meal_type === 'lunch');
                            const dinnerEntries = dayFoodEntries.filter(e => e.meal_type === 'dinner');
                            
                            // Create meal rows
                            const mealRows: Array<{
                              mealType: string;
                              foodNames: string;
                              glucose: number;
                              risk: string;
                            }> = [];
                            
                            if (breakfast.length > 0) {
                              const foodNames = breakfastEntries.map(e => e.food_name).join(', ') || 'Meal logged';
                              const avgGlucose = breakfast.reduce((sum, m) => sum + m.predicted_glucose_1hr, 0) / breakfast.length;
                              const highRisk = breakfast.some(m => m.risk_level === 'High');
                              const midRisk = breakfast.some(m => m.risk_level === 'Mid');
                              mealRows.push({
                                mealType: 'Breakfast',
                                foodNames,
                                glucose: avgGlucose,
                                risk: highRisk ? 'High' : midRisk ? 'Mid' : 'Low'
                              });
                            }
                            
                            if (lunch.length > 0) {
                              const foodNames = lunchEntries.map(e => e.food_name).join(', ') || 'Meal logged';
                              const avgGlucose = lunch.reduce((sum, m) => sum + m.predicted_glucose_1hr, 0) / lunch.length;
                              const highRisk = lunch.some(m => m.risk_level === 'High');
                              const midRisk = lunch.some(m => m.risk_level === 'Mid');
                              mealRows.push({
                                mealType: 'Lunch',
                                foodNames,
                                glucose: avgGlucose,
                                risk: highRisk ? 'High' : midRisk ? 'Mid' : 'Low'
                              });
                            }
                            
                            if (dinner.length > 0) {
                              const foodNames = dinnerEntries.map(e => e.food_name).join(', ') || 'Meal logged';
                              const avgGlucose = dinner.reduce((sum, m) => sum + m.predicted_glucose_1hr, 0) / dinner.length;
                              const highRisk = dinner.some(m => m.risk_level === 'High');
                              const midRisk = dinner.some(m => m.risk_level === 'Mid');
                              mealRows.push({
                                mealType: 'Dinner',
                                foodNames,
                                glucose: avgGlucose,
                                risk: highRisk ? 'High' : midRisk ? 'Mid' : 'Low'
                              });
                            }
                            
                            return (
                              <div key={dateKey} className="border-b border-[rgba(226,234,235,0.3)] pb-3 last:border-b-0 last:pb-0">
                                {mealRows.map((row, idx) => (
                                  <div key={idx} className="flex items-center gap-3 py-1.5">
                                    {/* Date - only show on first row */}
                                    <div className="w-14 flex-shrink-0">
                                      {idx === 0 && (
                                        <span className="text-[12px] font-semibold text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif" }}>
                                          {formattedDate}
                                        </span>
                                      )}
                                    </div>
                                    
                                    {/* Meal Type */}
                                    <div className="w-20 flex-shrink-0">
                                      <span className="text-[11px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>
                                        {row.mealType}
                                      </span>
                                    </div>
                                    
                                    {/* Food Names */}
                                    <div className="flex-1 min-w-0">
                                      <span className="text-[11px] text-[#0d2b35] truncate block" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>
                                        {row.foodNames}
                                      </span>
                                    </div>
                                    
                                    {/* Glucose */}
                                    <div className="w-16 flex-shrink-0 text-right">
                                      <span className="text-[13px] font-bold text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif" }}>
                                        {Math.round(row.glucose)}
                                      </span>
                                      <span className="text-[9px] text-[#637c84] ml-0.5" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>
                                        mg/dL
                                      </span>
                                    </div>
                                    
                                    {/* Risk Badge */}
                                    <div className="w-14 flex-shrink-0">
                                      {(() => {
                                        const riskColor = getRiskColor(row.risk);
                                        return (
                                          <span 
                                            className="px-2 py-0.5 rounded-md text-[10px] font-bold block text-center" 
                                            style={{ 
                                              backgroundColor: riskColor.bgColor,
                                              color: riskColor.color,
                                              fontFamily: "'Geist', sans-serif"
                                            }}
                                          >
                                            {row.risk}
                                          </span>
                                        );
                                      })()}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            );
                          });
                        })()}
                      </div>
                    </div>
                  )}

                  {/* Today's Meals */}
                  <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-6">
                    <div className="mb-4">
                      <h2 className="font-['Geist'] font-bold text-xl text-[#0d2b35] tracking-[-0.5px]">
                        Today's Nutrition
                      </h2>
                      <p className="font-['Nunito_Sans'] text-xs text-[#637c84]">
                        Daily summary
                      </p>
                    </div>
                    {dailySummary && dailySummary.total_calories > 0 ? (
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>Total Calories</span>
                          <span className="text-[16px] text-[#0d2b35] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                            {dailySummary.total_calories.toFixed(0)} kcal
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>Carbohydrates</span>
                          <span className="text-[16px] text-[#0d2b35] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                            {dailySummary.total_carbohydrates_g.toFixed(1)} g
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>Protein</span>
                          <span className="text-[16px] text-[#0d2b35] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                            {dailySummary.total_protein_g.toFixed(1)} g
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>Fat</span>
                          <span className="text-[16px] text-[#0d2b35] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                            {dailySummary.total_fat_g.toFixed(1)} g
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-[rgba(226,234,235,0.1)] rounded-2xl p-4 text-center">
                        <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito_Sans', sans-serif" }}>
                          No meals logged today
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <button
                      onClick={() => navigate('/log-meal')}
                      className="bg-[#1e6177] text-white rounded-xl p-4 border-none cursor-pointer shadow-sm hover:bg-[#1a5565] transition-colors"
                    >
                      <div className="flex flex-col items-center gap-1.5">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        <span className="text-[13px] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                          Log Meal
                        </span>
                      </div>
                    </button>
                    <button
                      onClick={() => navigate('/health-check')}
                      className="bg-white border-[0.8px] border-[#1e6177] text-[#1e6177] rounded-xl p-4 cursor-pointer shadow-sm hover:bg-[rgba(30,97,119,0.05)] transition-colors"
                    >
                      <div className="flex flex-col items-center gap-1.5">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <span className="text-[13px] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                          Health Check
                        </span>
                      </div>
                    </button>
                  </div>
                </>
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
            height_cm: profile?.height_cm || null,
            weight_kg: profile?.weight_kg || null,
            gender: profile?.gender || null,
            family_history: profile?.family_history || null
          }}
          lastHealthCheck={latestHealthCheck ? {
            weight_kg: latestHealthCheck.health_metrics?.weight_kg || profile?.weight_kg || 0,
            blood_sugar_mgdl: latestHealthCheck.health_metrics?.blood_sugar_mgdl || 0
          } : null}
        />
      </div>
    </ResponsiveLayout>
  );
}
