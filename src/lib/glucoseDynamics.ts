/**
 * Clinical Glucose Dynamics Service
 * 
 * Implements evidence-based glucose tracking with:
 * - Circadian rhythm effects (time-of-day)
 * - Glucose decay model (return to baseline)
 * - Age and gender adjustments
 * - Physiological factors
 * 
 * Based on clinical research and ADA 2024 guidelines
 */

export interface GlucoseDynamicsParams {
  predictedGlucose1hr: number;  // From RF #1 model
  baselineGlucose: number;       // Fasting glucose
  mealTime: Date;                // When meal was consumed
  currentTime: Date;             // Current time
  age: number;
  gender: 'male' | 'female';
  bmi: number;
  mealType?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
}

export interface GlucoseEstimate {
  currentGlucose: number;
  adjustedPeakGlucose: number;
  timeMultiplier: number;
  ageMultiplier: number;
  genderMultiplier: number;
  hoursSinceMeal: number;
  decayFactor: number;
  status: 'peak' | 'declining' | 'baseline';
  explanation: string;
}

/**
 * Get time-of-day multiplier based on circadian rhythm
 * Evidence: Van Cauter et al. (1997), Saad et al. (2012)
 */
function getTimeOfDayMultiplier(mealTime: Date, mealType?: string): number {
  const hour = mealTime.getHours();
  
  // Use meal type if provided, otherwise use time
  if (mealType) {
    switch (mealType) {
      case 'breakfast':
        return 1.15; // Dawn phenomenon - highest insulin resistance
      case 'lunch':
        return 0.90; // Peak insulin sensitivity
      case 'dinner':
        return 1.05; // Declining insulin sensitivity
      case 'snack':
        // Snacks follow time-of-day pattern
        break;
    }
  }
  
  // Time-based multipliers (for snacks or when meal type not specified)
  if (hour >= 6 && hour < 9) {
    return 1.15; // Early morning (dawn phenomenon)
  } else if (hour >= 9 && hour < 11) {
    return 1.10; // Late morning
  } else if (hour >= 11 && hour < 15) {
    return 0.90; // Midday (best insulin sensitivity)
  } else if (hour >= 15 && hour < 18) {
    return 1.0;  // Afternoon (baseline)
  } else if (hour >= 18 && hour < 20) {
    return 1.05; // Early evening
  } else if (hour >= 20 && hour < 22) {
    return 1.10; // Late evening
  } else {
    return 1.20; // Night (worst insulin sensitivity)
  }
}

/**
 * Get age-based multiplier
 * Evidence: DeFronzo (1981) - insulin sensitivity declines ~1% per year after 30
 */
function getAgeMultiplier(age: number): number {
  if (age < 30) {
    return 1.0;
  } else if (age < 45) {
    return 1.05;
  } else if (age < 60) {
    return 1.10;
  } else if (age < 75) {
    return 1.15;
  } else {
    return 1.20;
  }
}

/**
 * Get gender-based multiplier
 * Evidence: Valdes & Elkind-Hirsch (1991), Carr (2003)
 * 
 * Note: For simplicity, using average multiplier for females
 * Future enhancement: Track menstrual cycle for premenopausal women
 */
function getGenderMultiplier(gender: 'male' | 'female', age: number): number {
  if (gender === 'male') {
    return 1.0;
  } else {
    // Postmenopausal (typically age 50+)
    if (age >= 50) {
      return 1.10;
    }
    // Premenopausal (average across cycle)
    return 1.0;
  }
}

/**
 * Calculate glucose decay factor
 * Evidence: Wolever et al. (1991), Caumo et al. (2000)
 * 
 * Uses exponential decay: e^(-t/τ)
 * where τ (tau) is the time constant
 */
function getDecayFactor(hoursSinceMeal: number, bmi: number): number {
  // Determine time constant based on metabolic health (approximated by BMI)
  let tau: number;
  
  if (bmi < 25) {
    tau = 1.5; // Healthy individuals
  } else if (bmi < 30) {
    tau = 1.8; // Overweight
  } else {
    tau = 2.2; // Obese (slower glucose clearance)
  }
  
  // Exponential decay formula
  return Math.exp(-hoursSinceMeal / tau);
}

/**
 * Calculate current glucose level with clinical adjustments
 */
export function calculateCurrentGlucose(params: GlucoseDynamicsParams): GlucoseEstimate {
  const {
    predictedGlucose1hr,
    baselineGlucose,
    mealTime,
    currentTime,
    age,
    gender,
    bmi,
    mealType
  } = params;
  
  // Calculate time since meal
  const timeDiffMs = currentTime.getTime() - mealTime.getTime();
  const hoursSinceMeal = timeDiffMs / (1000 * 60 * 60);
  
  // Get multipliers
  const timeMultiplier = getTimeOfDayMultiplier(mealTime, mealType);
  const ageMultiplier = getAgeMultiplier(age);
  const genderMultiplier = getGenderMultiplier(gender, age);
  
  // Apply multipliers to RF #1 prediction
  const adjustedPeakGlucose = predictedGlucose1hr * timeMultiplier * ageMultiplier * genderMultiplier;
  
  // Calculate current glucose based on time since meal
  let currentGlucose: number;
  let status: 'peak' | 'declining' | 'baseline';
  let explanation: string;
  
  if (hoursSinceMeal < 0.5) {
    // Less than 30 minutes - glucose is rising
    // Linear interpolation from baseline to peak
    const progress = hoursSinceMeal / 0.5;
    currentGlucose = baselineGlucose + (adjustedPeakGlucose - baselineGlucose) * progress;
    status = 'peak';
    explanation = 'Glucose is rising after meal';
  } else if (hoursSinceMeal <= 1.5) {
    // 30-90 minutes - at or near peak
    currentGlucose = adjustedPeakGlucose;
    status = 'peak';
    explanation = 'At peak glucose level (1-hour post-meal)';
  } else if (hoursSinceMeal < 5) {
    // 1.5-5 hours - declining toward baseline
    const decayFactor = getDecayFactor(hoursSinceMeal - 1, bmi);
    const elevation = (adjustedPeakGlucose - baselineGlucose) * decayFactor;
    currentGlucose = baselineGlucose + elevation;
    status = 'declining';
    
    const percentOfPeak = (decayFactor * 100).toFixed(0);
    explanation = `Glucose declining (${percentOfPeak}% of peak elevation)`;
  } else {
    // 5+ hours - returned to baseline
    currentGlucose = baselineGlucose;
    status = 'baseline';
    explanation = 'Glucose returned to baseline';
  }
  
  return {
    currentGlucose: Math.round(currentGlucose),
    adjustedPeakGlucose: Math.round(adjustedPeakGlucose),
    timeMultiplier,
    ageMultiplier,
    genderMultiplier,
    hoursSinceMeal,
    decayFactor: hoursSinceMeal >= 1.5 ? getDecayFactor(hoursSinceMeal - 1, bmi) : 1.0,
    status,
    explanation
  };
}

/**
 * Get user-friendly time description
 */
export function getTimeSinceMealDescription(hoursSinceMeal: number): string {
  if (hoursSinceMeal < 0.5) {
    return 'just now';
  } else if (hoursSinceMeal < 1) {
    const minutes = Math.round(hoursSinceMeal * 60);
    return `${minutes} min ago`;
  } else if (hoursSinceMeal < 2) {
    return '1 hour ago';
  } else {
    const hours = Math.floor(hoursSinceMeal);
    return `${hours} hours ago`;
  }
}

/**
 * Determine if meal prediction is still relevant
 * Meals older than 5 hours have returned to baseline
 */
export function isMealPredictionRelevant(mealTime: Date, currentTime: Date): boolean {
  const hoursSinceMeal = (currentTime.getTime() - mealTime.getTime()) / (1000 * 60 * 60);
  return hoursSinceMeal < 5;
}
