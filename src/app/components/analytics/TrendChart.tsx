/**
 * Trend Chart Component
 * 
 * Displays nutritional trends over time using Recharts.
 * Supports line charts for calories and area charts for macronutrients.
 */

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { AlertCircle } from 'lucide-react';
import { fetchNutritionalTrends, NutritionalTrends } from '../../../lib/analyticsApi';

interface TrendChartProps {
  startDate?: string;
  endDate?: string;
  chartType?: 'calories' | 'macronutrients';
}

export default function TrendChart({ 
  startDate, 
  endDate, 
  chartType = 'calories' 
}: TrendChartProps) {
  const [trends, setTrends] = useState<NutritionalTrends | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTrends();
  }, [startDate, endDate]);

  const loadTrends = async () => {
    try {
      setLoading(true);
      setError(null);

      // Default to last 7 days if no dates provided
      const end = endDate || new Date().toISOString().split('T')[0];
      const start = startDate || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const data = await fetchNutritionalTrends(start, end);
      setTrends(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load trends');
      console.error('Error loading trends:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-[200px] bg-gray-200 rounded"></div>
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

  if (!trends || trends.daily_data.length === 0) {
    return (
      <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
        <p 
          className="text-[14px] text-[#637c84] text-center" 
          style={{ fontFamily: "'Nunito Sans', sans-serif" }}
        >
          No data available for the selected period
        </p>
      </div>
    );
  }

  // Format data for charts
  const chartData = trends.daily_data.map((day) => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    calories: Math.round(day.calories),
    protein: Math.round(day.protein_g),
    carbs: Math.round(day.carbohydrates_g),
    fat: Math.round(day.fat_g),
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-xl shadow-lg p-3">
          <p 
            className="text-[12px] text-[#0d2b35] font-semibold mb-2" 
            style={{ fontFamily: "'Geist', sans-serif" }}
          >
            {label}
          </p>
          {payload.map((entry: any, index: number) => (
            <p 
              key={index}
              className="text-[11px]" 
              style={{ 
                fontFamily: "'Nunito Sans', sans-serif",
                color: entry.color 
              }}
            >
              {entry.name}: {entry.value}{entry.unit || ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5">
      <p 
        className="text-[14px] text-[#637c84] uppercase tracking-[0.7px] mb-4" 
        style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
      >
        {chartType === 'calories' ? 'Calorie Intake Trend' : 'Macronutrient Trends'}
      </p>

      {chartType === 'calories' ? (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(226,234,235,0.5)" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 11, fill: '#637c84', fontFamily: "'Nunito Sans', sans-serif" }}
              stroke="#e2eaeb"
            />
            <YAxis 
              tick={{ fontSize: 11, fill: '#637c84', fontFamily: "'Nunito Sans', sans-serif" }}
              stroke="#e2eaeb"
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="calories" 
              stroke="#8aab9f" 
              strokeWidth={2}
              dot={{ fill: '#8aab9f', r: 4 }}
              activeDot={{ r: 6 }}
              name="Calories"
              unit=" kcal"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(226,234,235,0.5)" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 11, fill: '#637c84', fontFamily: "'Nunito Sans', sans-serif" }}
              stroke="#e2eaeb"
            />
            <YAxis 
              tick={{ fontSize: 11, fill: '#637c84', fontFamily: "'Nunito Sans', sans-serif" }}
              stroke="#e2eaeb"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ 
                fontSize: '11px', 
                fontFamily: "'Nunito Sans', sans-serif" 
              }}
            />
            <Area 
              type="monotone" 
              dataKey="protein" 
              stackId="1"
              stroke="#8aab9f" 
              fill="#8aab9f"
              fillOpacity={0.6}
              name="Protein"
              unit="g"
            />
            <Area 
              type="monotone" 
              dataKey="carbs" 
              stackId="1"
              stroke="#f59e0b" 
              fill="#f59e0b"
              fillOpacity={0.6}
              name="Carbs"
              unit="g"
            />
            <Area 
              type="monotone" 
              dataKey="fat" 
              stackId="1"
              stroke="#637c84" 
              fill="#637c84"
              fillOpacity={0.6}
              name="Fat"
              unit="g"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* Average Stats */}
      <div className="mt-4 pt-4 border-t border-[rgba(226,234,235,0.3)]">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p 
              className="text-[10px] text-[#637c84] uppercase tracking-[0.5px] mb-1" 
              style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 700 }}
            >
              Avg Calories
            </p>
            <p 
              className="text-[18px] text-[#0d2b35]" 
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
            >
              {Math.round(trends.avg_calories)}
            </p>
          </div>
          <div>
            <p 
              className="text-[10px] text-[#637c84] uppercase tracking-[0.5px] mb-1" 
              style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 700 }}
            >
              Avg Carbs
            </p>
            <p 
              className="text-[18px] text-[#0d2b35]" 
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
            >
              {Math.round(trends.avg_carbohydrates_g)}g
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
