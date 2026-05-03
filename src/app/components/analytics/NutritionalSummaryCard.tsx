/**
 * Nutritional Summary Card Component
 * 
 * Displays nutritional summary with time period selection,
 * macronutrient breakdown, and carbohydrate warnings.
 */

import { useState, useEffect } from 'react';
import { AlertCircle, Calendar } from 'lucide-react';
import { fetchPeriodSummary, PeriodSummary } from '../../../lib/analyticsApi';

interface NutritionalSummaryCardProps {
  onPeriodChange?: (period: 'daily' | 'weekly' | 'monthly') => void;
}

export default function NutritionalSummaryCard({ onPeriodChange }: NutritionalSummaryCardProps) {
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');
  const [summary, setSummary] = useState<PeriodSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, [period]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Use today's date as reference
      const today = new Date().toISOString().split('T')[0];
      const data = await fetchPeriodSummary(period, today);
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load summary');
      console.error('Error loading summary:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = (newPeriod: 'daily' | 'weekly' | 'monthly') => {
    setPeriod(newPeriod);
    onPeriodChange?.(newPeriod);
  };

  if (loading) {
    return (
      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
        <div className="flex items-center gap-2 text-red-600">
          <AlertCircle size={20} />
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
      {/* Period Selector */}
      <div className="flex items-center justify-between mb-4">
        <p 
          className="text-[14px] text-[#637c84] uppercase tracking-[0.7px]" 
          style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
        >
          Nutritional Summary
        </p>
        <div className="flex gap-2">
          {(['daily', 'weekly', 'monthly'] as const).map((p) => (
            <button
              key={p}
              onClick={() => handlePeriodChange(p)}
              className={`px-3 py-1 rounded-lg text-[12px] transition-colors ${
                period === p
                  ? 'bg-[#8aab9f] text-white'
                  : 'bg-[rgba(226,234,235,0.3)] text-[#637c84]'
              }`}
              style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Date Range */}
      <div className="flex items-center gap-2 mb-4 text-[12px] text-[#637c84]">
        <Calendar size={14} />
        <span style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
          {summary.start_date} to {summary.end_date}
        </span>
      </div>

      {/* Calories Summary */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-1">
          <p 
            className="text-[32px] text-[#0d2b35]" 
            style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
          >
            {Math.round(summary.avg_daily_calories)}
          </p>
          <p 
            className="text-[14px] text-[#637c84]" 
            style={{ fontFamily: "'Nunito Sans', sans-serif" }}
          >
            kcal/day avg
          </p>
        </div>
        <p 
          className="text-[12px] text-[#8aab9f]" 
          style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
        >
          {Math.round(summary.total_calories)} total calories over {summary.days_with_data} days
        </p>
      </div>

      {/* Macronutrient Breakdown */}
      <div className="mb-4">
        <p 
          className="text-[12px] text-[#637c84] uppercase tracking-[0.5px] mb-3" 
          style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 700 }}
        >
          Macronutrient Distribution
        </p>
        
        {/* Macronutrient Bars */}
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span style={{ fontFamily: "'Nunito Sans', sans-serif", color: '#637c84' }}>
                Protein
              </span>
              <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600, color: '#0d2b35' }}>
                {summary.macronutrient_distribution.protein_percent.toFixed(1)}%
              </span>
            </div>
            <div className="h-2 bg-[rgba(226,234,235,0.3)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#8aab9f] rounded-full transition-all duration-300"
                style={{ width: `${summary.macronutrient_distribution.protein_percent}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span style={{ fontFamily: "'Nunito Sans', sans-serif", color: '#637c84' }}>
                Carbohydrates
              </span>
              <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600, color: '#0d2b35' }}>
                {summary.macronutrient_distribution.carbohydrates_percent.toFixed(1)}%
              </span>
            </div>
            <div className="h-2 bg-[rgba(226,234,235,0.3)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#f59e0b] rounded-full transition-all duration-300"
                style={{ width: `${summary.macronutrient_distribution.carbohydrates_percent}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span style={{ fontFamily: "'Nunito Sans', sans-serif", color: '#637c84' }}>
                Fat
              </span>
              <span style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600, color: '#0d2b35' }}>
                {summary.macronutrient_distribution.fat_percent.toFixed(1)}%
              </span>
            </div>
            <div className="h-2 bg-[rgba(226,234,235,0.3)] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#637c84] rounded-full transition-all duration-300"
                style={{ width: `${summary.macronutrient_distribution.fat_percent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Carbohydrate Warnings */}
      {summary.warnings.length > 0 && (
        <div className="mt-4 space-y-2">
          {summary.warnings.map((warning, index) => (
            <div
              key={index}
              className={`p-3 rounded-xl border-[0.8px] ${
                warning.severity === 'high'
                  ? 'bg-red-50 border-red-200'
                  : 'bg-orange-50 border-orange-200'
              }`}
            >
              <div className="flex items-start gap-2">
                <AlertCircle 
                  size={16} 
                  className={warning.severity === 'high' ? 'text-red-600' : 'text-orange-600'}
                />
                <div className="flex-1">
                  <p 
                    className={`text-[11px] font-semibold mb-1 ${
                      warning.severity === 'high' ? 'text-red-700' : 'text-orange-700'
                    }`}
                    style={{ fontFamily: "'Nunito Sans', sans-serif" }}
                  >
                    {warning.date}: {warning.carbohydrates_g.toFixed(0)}g carbs
                  </p>
                  <p 
                    className={`text-[10px] ${
                      warning.severity === 'high' ? 'text-red-600' : 'text-orange-600'
                    }`}
                    style={{ fontFamily: "'Nunito Sans', sans-serif" }}
                  >
                    {warning.message}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
