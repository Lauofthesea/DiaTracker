import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, UtensilsCrossed, Trash2, Loader2 } from "lucide-react";
import ResponsiveLayout from "./ResponsiveLayout";
import { getFoodEntries, getDailySummary, deleteFoodEntry } from "../../lib/foodApi";
import type { FoodEntry, DailyNutritionalSummary } from "../../types/food";

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const entryDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  if (entryDay.getTime() === today.getTime()) return "Today";
  if (entryDay.getTime() === yesterday.getTime()) return "Yesterday";
  return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
}

function isWithin7Days(dateStr: string): boolean {
  const entryDate = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - entryDate.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);
  return diffDays <= 7;
}

const typeColors: Record<string, string> = {
  breakfast: "#f59e0b",
  lunch: "#1e6177",
  dinner: "#8b5cf6",
  snack: "#8aab9f",
};

export default function MealHistoryPage() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState<FoodEntry[]>([]);
  const [filterType, setFilterType] = useState<string>("All");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [todaySummary, setTodaySummary] = useState<DailyNutritionalSummary | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Load food entries
  useEffect(() => {
    loadEntries();
    loadTodaySummary();
  }, []);

  const loadEntries = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get entries from the last 30 days
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 30);

      const response = await getFoodEntries({
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        page: 1,
        page_size: 100,
      });

      setEntries(response.entries);
    } catch (err) {
      console.error("Error loading entries:", err);
      setError(err instanceof Error ? err.message : "Failed to load meal history");
    } finally {
      setIsLoading(false);
    }
  };

  const loadTodaySummary = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const summary = await getDailySummary(today);
      setTodaySummary(summary);
    } catch (err) {
      console.error("Error loading today's summary:", err);
      // Don't show error for summary, it's not critical
    }
  };

  const handleDelete = async (entryId: string, consumedAt: string) => {
    if (!isWithin7Days(consumedAt)) {
      setError("Cannot delete entries older than 7 days");
      setTimeout(() => setError(null), 3000);
      return;
    }

    if (!confirm("Are you sure you want to delete this entry?")) {
      return;
    }

    setDeletingId(entryId);
    setError(null);

    try {
      await deleteFoodEntry(entryId);
      // Remove from local state
      setEntries((prev) => prev.filter((e) => e.entry_id !== entryId));
      // Reload today's summary
      loadTodaySummary();
    } catch (err) {
      console.error("Error deleting entry:", err);
      setError(err instanceof Error ? err.message : "Failed to delete entry");
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = filterType === "All" ? entries : entries.filter((e) => e.meal_type === filterType.toLowerCase());

  // Group by date
  const grouped: Record<string, FoodEntry[]> = {};
  filtered.forEach((entry) => {
    const key = formatDate(entry.consumed_at);
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(entry);
  });

  // Sort entries within each group by time descending
  Object.values(grouped).forEach((arr) => arr.sort((a, b) => new Date(b.consumed_at).getTime() - new Date(a.consumed_at).getTime()));

  const totalToday = todaySummary?.total_calories || 0;
  const totalCarbsToday = todaySummary?.total_carbohydrates_g || 0;
  const mealsToday = entries.filter((e) => formatDate(e.consumed_at) === "Today").length;

  return (
    <ResponsiveLayout>
      <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto relative">
        {/* Header */}
        <div className="sticky top-0 z-40 backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-b-[0.8px] border-solid border-[rgba(226,234,235,0.4)] px-4 sm:px-6 py-4">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <button onClick={() => navigate("/")} className="bg-[rgba(226,234,235,0.5)] rounded-full w-10 h-10 flex items-center justify-center cursor-pointer border-none md:hidden">
              <ArrowLeft size={24} className="text-[#0d2b35]" />
            </button>
            <p className="text-[20px] text-[#0d2b35] tracking-[-0.5px]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
              Meal History
            </p>
          </div>
        </div>

        <div className="px-4 sm:px-6 pt-4 pb-6 max-w-7xl mx-auto">{/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-2xl mb-4">
            {error}
          </div>
        )}

        {/* Today's Summary */}
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-3xl shadow-sm p-5 mb-4">
          <p className="text-[12px] text-[#637c84] uppercase tracking-[0.6px] mb-3" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
            Today's Summary
          </p>
          <div className="flex gap-4">
            <div className="flex-1 text-center">
              <p className="text-[24px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                {Math.round(totalToday)}
              </p>
              <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>kcal consumed</p>
            </div>
            <div className="w-[1px] bg-[rgba(226,234,235,0.5)]" />
            <div className="flex-1 text-center">
              <p className="text-[24px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                {Math.round(totalCarbsToday)}g
              </p>
              <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>carbs</p>
            </div>
            <div className="w-[1px] bg-[rgba(226,234,235,0.5)]" />
            <div className="flex-1 text-center">
              <p className="text-[24px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                {mealsToday}
              </p>
              <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>meals</p>
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="flex gap-2 mb-4 overflow-x-auto">
          {["All", "Breakfast", "Lunch", "Dinner", "Snack"].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`h-[34px] px-4 rounded-full border-[0.8px] cursor-pointer text-[13px] whitespace-nowrap ${
                filterType === t
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 500 }}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 size={48} className="text-[#1e6177] animate-spin mb-3" />
            <p className="text-[16px] text-[#637c84]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
              Loading meal history...
            </p>
          </div>
        )}

        {/* Grouped Entries */}
        {!isLoading && Object.entries(grouped).map(([dateLabel, dateEntries]) => (
          <div key={dateLabel} className="mb-5">
            <p className="text-[12px] text-[#637c84] uppercase tracking-[0.6px] mb-2" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
              {dateLabel}
            </p>
            <div className="flex flex-col gap-2">
              {dateEntries.map((entry) => {
                const canDelete = isWithin7Days(entry.consumed_at);
                return (
                  <div key={entry.entry_id} className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-sm p-3 flex items-center gap-3">
                    <div
                      className="w-[44px] h-[44px] rounded-xl flex items-center justify-center shrink-0"
                      style={{ backgroundColor: `${typeColors[entry.meal_type]}15` }}
                    >
                      <UtensilsCrossed size={20} style={{ color: typeColors[entry.meal_type] }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[14px] text-[#0d2b35] truncate" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                        {entry.food_name}
                      </p>
                      <div className="flex items-center gap-2">
                        <span
                          className="text-[10px] px-[6px] py-[1px] rounded-full capitalize"
                          style={{
                            backgroundColor: `${typeColors[entry.meal_type]}20`,
                            color: typeColors[entry.meal_type],
                            fontFamily: "'Nunito Sans', sans-serif",
                            fontWeight: 700,
                          }}
                        >
                          {entry.meal_type}
                        </span>
                        <span className="text-[11px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                          {formatTime(entry.consumed_at)}
                        </span>
                        <span className="text-[11px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                          {entry.quantity}{entry.unit}
                        </span>
                      </div>
                    </div>
                    <div className="text-right mr-1">
                      <p className="text-[14px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}>
                        {Math.round(entry.nutritional_totals.calories)} <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                      </p>
                      <p className="text-[10px] text-[#8aab9f] uppercase" style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 700 }}>
                        {Math.round(entry.nutritional_totals.carbohydrates_g)}g carbs
                      </p>
                    </div>
                    <button
                      onClick={() => handleDelete(entry.entry_id, entry.consumed_at)}
                      disabled={!canDelete || deletingId === entry.entry_id}
                      title={canDelete ? "Delete entry" : "Cannot delete entries older than 7 days"}
                      className={`w-7 h-7 rounded-full flex items-center justify-center border-none shrink-0 ${
                        canDelete
                          ? "bg-[rgba(239,68,68,0.08)] cursor-pointer"
                          : "bg-[rgba(99,124,132,0.08)] cursor-not-allowed opacity-50"
                      }`}
                    >
                      {deletingId === entry.entry_id ? (
                        <Loader2 size={14} className="text-[#ef4444] animate-spin" />
                      ) : (
                        <Trash2 size={14} className={canDelete ? "text-[#ef4444]" : "text-[#637c84]"} />
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* Empty State */}
        {!isLoading && filtered.length === 0 && (
          <div className="text-center py-12">
            <UtensilsCrossed size={48} className="text-[rgba(226,234,235,0.6)] mx-auto mb-3" />
            <p className="text-[16px] text-[#637c84]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
              No meals logged yet
            </p>
            <p className="text-[13px] text-[#637c84] mt-1" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
              Start logging meals to see your history
            </p>
          </div>
        )}
      </div>
    </div>
    </ResponsiveLayout>
  );
}
