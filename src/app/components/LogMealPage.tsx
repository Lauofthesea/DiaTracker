import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router";
import {
  ArrowLeft,
  Search,
  PenLine,
  X,
  Plus,
  Minus,
  Loader2,
} from "lucide-react";
import ResponsiveLayout from "./ResponsiveLayout";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { searchFoods, createFoodEntry } from "../../lib/foodApi";
import type { FoodSearchResult } from "../../types/food";

type MealType = "breakfast" | "lunch" | "dinner" | "snack";

interface MealItem {
  id: string;
  food_id: string;
  name: string;
  serving: string;
  kcal: number;
  carbs: number;
  image: string;
  type: MealType;
}

export default function LogMealPage() {
  const navigate = useNavigate();
  const [selectedType, setSelectedType] = useState<MealType>("breakfast");
  const [addedItems, setAddedItems] = useState<MealItem[]>([]);
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualName, setManualName] = useState("");
  const [manualServing, setManualServing] = useState("");
  const [manualKcal, setManualKcal] = useState("");
  const [manualCarbs, setManualCarbs] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<FoodSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const mealTypes: MealType[] = ["breakfast", "lunch", "dinner", "snack"];

  // Debounced search function
  const performSearch = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const response = await searchFoods({
        q: query,
        page: 1,
        page_size: 20,
      });
      setSearchResults(response.foods);
    } catch (err) {
      console.error("Search error:", err);
      setError(err instanceof Error ? err.message : "Failed to search foods");
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, performSearch]);

  const totalCalories = addedItems.reduce((sum, i) => sum + i.kcal, 0);
  const totalCarbs = addedItems.reduce((sum, i) => sum + i.carbs, 0);
  const glImpact = totalCarbs < 20 ? "Low" : totalCarbs < 45 ? "Medium" : "High";
  const glColor =
    glImpact === "Low" ? "#8aab9f" : glImpact === "Medium" ? "#f59e0b" : "#ef4444";

  const addFoodItem = (food: FoodSearchResult) => {
    const item: MealItem = {
      id: `${food.food_id}-${Date.now()}`,
      food_id: food.food_id,
      name: food.name,
      serving: "100g", // Default serving
      kcal: food.calories_per_serving || 0,
      carbs: 0, // Will be calculated from nutritional data
      image: "",
      type: selectedType,
    };
    setAddedItems((prev) => [...prev, item]);
  };

  const removeItem = (id: string) => {
    setAddedItems((prev) => prev.filter((i) => i.id !== id));
  };

  const submitManual = () => {
    if (!manualName || !manualKcal) return;
    const item: MealItem = {
      id: "manual-" + Date.now(),
      food_id: "", // Manual entries don't have a food_id
      name: manualName,
      serving: manualServing || "1 serving",
      kcal: parseInt(manualKcal) || 0,
      carbs: parseInt(manualCarbs) || 0,
      image: "",
      type: selectedType,
    };
    setAddedItems((prev) => [...prev, item]);
    setManualName("");
    setManualServing("");
    setManualKcal("");
    setManualCarbs("");
    setShowManualEntry(false);
  };

  const handleConfirmMeal = async () => {
    if (addedItems.length === 0) return;

    setIsSubmitting(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Create food entries for each item
      const timestamp = new Date().toISOString();
      
      for (const item of addedItems) {
        // Skip manual entries without food_id for now
        if (!item.food_id) {
          console.warn("Skipping manual entry:", item.name);
          continue;
        }

        await createFoodEntry({
          food_id: item.food_id,
          quantity: 100, // Default quantity
          unit: "g",
          meal_type: item.type,
          consumed_at: timestamp,
        });
      }

      setSuccessMessage("Meal logged successfully!");
      setAddedItems([]);
      
      // Navigate to history after a short delay
      setTimeout(() => {
        navigate("/history");
      }, 1500);
    } catch (err) {
      console.error("Error creating food entries:", err);
      setError(err instanceof Error ? err.message : "Failed to log meal");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ResponsiveLayout>
      <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto relative">
        {/* Header */}
        <div className="sticky top-0 z-40 backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-b-[0.8px] border-solid border-[rgba(226,234,235,0.4)] px-4 sm:px-6 py-4">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <button
              onClick={() => navigate("/")}
              className="bg-[rgba(226,234,235,0.5)] rounded-full w-10 h-10 flex items-center justify-center cursor-pointer border-none md:hidden"
            >
              <ArrowLeft size={24} className="text-[#0d2b35]" />
            </button>
            <p
              className="text-[20px] text-[#0d2b35] tracking-[-0.5px]"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 600,
              }}
            >
              Log New Meal
            </p>
          </div>
        </div>

        <div className="px-4 sm:px-6 pb-[160px] md:pb-6 pt-4 overflow-auto max-w-7xl mx-auto">{/* Error/Success Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-2xl mb-4">
            {error}
          </div>
        )}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-2xl mb-4">
            {successMessage}
          </div>
        )}

        {/* Search */}
        <div className="bg-white border-[0.8px] border-[rgba(226,234,235,0.5)] rounded-2xl shadow-sm flex items-center px-4 h-[52px] mb-3">
          <Search size={20} className="text-[#637c84] mr-3" />
          <input
            type="text"
            placeholder="Search for food items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-[16px] text-[#0d2b35] placeholder:text-[rgba(13,43,53,0.5)]"
            style={{ fontFamily: "'Nunito Sans', sans-serif" }}
          />
          {isSearching && <Loader2 size={20} className="text-[#637c84] animate-spin" />}
        </div>

        {/* Manual Entry Button */}
        <div className="flex justify-center mb-5">
          <button
            onClick={() => setShowManualEntry(true)}
            className="bg-white border-[0.8px] border-[rgba(226,234,235,0.5)] rounded-2xl shadow-sm flex items-center gap-2 px-5 h-[52px] cursor-pointer"
          >
            <PenLine size={18} className="text-[#0d2b35]" />
            <span
              className="text-[16px] text-[#0d2b35]"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 500,
              }}
            >
              Manual Entry
            </span>
          </button>
        </div>

        {/* Manual Entry Modal */}
        {showManualEntry && (
          <div
            className="fixed inset-0 bg-black/30 z-50 flex items-end justify-center"
            onClick={() => setShowManualEntry(false)}
          >
            <div
              className="bg-white rounded-t-3xl w-full max-w-[430px] p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-5">
                <p
                  className="text-[18px] text-[#0d2b35]"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  Manual Entry
                </p>
                <button
                  onClick={() => setShowManualEntry(false)}
                  className="bg-transparent border-none cursor-pointer"
                >
                  <X size={24} className="text-[#637c84]" />
                </button>
              </div>
              <div className="flex flex-col gap-3">
                <input
                  placeholder="Food name *"
                  value={manualName}
                  onChange={(e) => setManualName(e.target.value)}
                  className="h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                />
                <input
                  placeholder="Serving size (e.g. 250g)"
                  value={manualServing}
                  onChange={(e) => setManualServing(e.target.value)}
                  className="h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                />
                <div className="flex gap-3">
                  <input
                    placeholder="Calories (kcal) *"
                    type="number"
                    value={manualKcal}
                    onChange={(e) => setManualKcal(e.target.value)}
                    className="flex-1 h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                  />
                  <input
                    placeholder="Carbs (g)"
                    type="number"
                    value={manualCarbs}
                    onChange={(e) => setManualCarbs(e.target.value)}
                    className="flex-1 h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                  />
                </div>
                <button
                  onClick={submitManual}
                  disabled={!manualName || !manualKcal}
                  className="h-[52px] bg-[#1e6177] text-white rounded-2xl border-none cursor-pointer text-[16px] disabled:opacity-50"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  Add Item
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Meal Type */}
        <div className="mb-4">
          <p
            className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
            style={{
              fontFamily: "'Geist', sans-serif",
              fontWeight: 700,
            }}
          >
            Meal Type
          </p>
          <div className="flex gap-2">
            {mealTypes.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] capitalize ${
                  selectedType === type
                    ? "bg-[#1e6177] border-[#1e6177] text-white"
                    : "bg-white border-[#e2eaeb] text-[#637c84]"
                }`}
                style={{
                  fontFamily: "'Nunito Sans', sans-serif",
                  fontWeight: 500,
                }}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Search Results */}
        {searchQuery && searchResults.length > 0 && (
          <div className="mb-4">
            <p
              className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 700,
              }}
            >
              Search Results
            </p>
            <div className="flex flex-col gap-2">
              {searchResults.map((food) => (
                <div
                  key={food.food_id}
                  className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-sm flex items-center p-3 gap-3"
                >
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-[14px] text-[#0d2b35] truncate"
                      style={{
                        fontFamily: "'Geist', sans-serif",
                        fontWeight: 600,
                      }}
                    >
                      {food.name}
                    </p>
                    <p
                      className="text-[12px] text-[#637c84]"
                      style={{
                        fontFamily: "'Nunito Sans', sans-serif",
                      }}
                    >
                      {food.category}
                    </p>
                  </div>
                  <div className="text-right mr-1">
                    <p
                      className="text-[14px] text-[#0d2b35]"
                      style={{
                        fontFamily: "'Geist', sans-serif",
                        fontWeight: 700,
                      }}
                    >
                      {food.calories_per_serving?.toFixed(0) || "N/A"}{" "}
                      <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                    </p>
                  </div>
                  <button
                    onClick={() => addFoodItem(food)}
                    className="bg-[rgba(30,97,119,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0"
                  >
                    <Plus size={16} className="text-[#1e6177]" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Added Items */}
        {addedItems.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <p
                className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 700,
                }}
              >
                Added Items ({addedItems.length})
              </p>
              <button
                onClick={() => setAddedItems([])}
                className="text-[12px] text-[#1e6177] underline bg-transparent border-none cursor-pointer"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                Clear All
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {addedItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-sm flex items-center p-3 gap-3"
                >
                  {item.image ? (
                    <ImageWithFallback
                      src={item.image}
                      alt={item.name}
                      className="w-[48px] h-[48px] rounded-xl object-cover shrink-0"
                    />
                  ) : (
                    <div className="w-[48px] h-[48px] rounded-xl bg-[rgba(226,234,235,0.3)] flex items-center justify-center shrink-0">
                      <PenLine size={20} className="text-[#637c84]" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p
                      className="text-[14px] text-[#0d2b35] truncate"
                      style={{
                        fontFamily: "'Geist', sans-serif",
                        fontWeight: 600,
                      }}
                    >
                      {item.name}
                    </p>
                    <p
                      className="text-[12px] text-[#637c84]"
                      style={{
                        fontFamily: "'Nunito Sans', sans-serif",
                      }}
                    >
                      {item.serving}
                    </p>
                  </div>
                  <div className="text-right mr-1">
                    <p
                      className="text-[14px] text-[#0d2b35]"
                      style={{
                        fontFamily: "'Geist', sans-serif",
                        fontWeight: 700,
                      }}
                    >
                      {item.kcal}{" "}
                      <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                    </p>
                    <p
                      className="text-[10px] text-[#8aab9f] uppercase"
                      style={{
                        fontFamily: "'Nunito Sans', sans-serif",
                        fontWeight: 700,
                      }}
                    >
                      {item.carbs}g Carbs
                    </p>
                  </div>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="bg-[rgba(239,68,68,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0"
                  >
                    <Minus size={16} className="text-[#ef4444]" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Meal Summary */}
        {addedItems.length > 0 && (
          <div className="bg-[rgba(214,230,225,0.4)] rounded-3xl p-6 mb-4">
            <p
              className="text-center text-[16px] text-[#204a3a] mb-4"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 700,
              }}
            >
              Meal Summary Prediction
            </p>
            <div className="flex justify-between">
              <div className="text-center flex-1">
                <p
                  className="text-[10px] text-[rgba(32,74,58,0.6)] uppercase tracking-[0.5px] mb-1"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Total Calories
                </p>
                <p
                  className="text-[24px] text-[#204a3a]"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  {totalCalories}
                </p>
              </div>
              <div className="text-center flex-1 border-x-[0.8px] border-[rgba(32,74,58,0.1)]">
                <p
                  className="text-[10px] text-[rgba(32,74,58,0.6)] uppercase tracking-[0.5px] mb-1"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Net Carbs
                </p>
                <p
                  className="text-[24px] text-[#204a3a]"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  {totalCarbs}
                  <span className="text-[12px]">g</span>
                </p>
              </div>
              <div className="text-center flex-1">
                <p
                  className="text-[10px] text-[rgba(32,74,58,0.6)] uppercase tracking-[0.5px] mb-1"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  GL Impact
                </p>
                <p
                  className="text-[24px]"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                    color: glColor,
                  }}
                >
                  {glImpact}
                </p>
              </div>
            </div>

            {/* Glucose Prediction bar */}
            <div className="bg-[rgba(255,255,255,0.6)] rounded-2xl p-4 mt-4">
              <div className="flex justify-between mb-2">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  Glucose Prediction
                </p>
                <p
                  className="text-[12px] text-[#8aab9f] tracking-[0.6px] uppercase"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  {glImpact === "Low"
                    ? "Stable Range"
                    : glImpact === "Medium"
                      ? "Moderate"
                      : "Elevated"}
                </p>
              </div>
              <div className="bg-[rgba(226,234,235,0.3)] h-2 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min((totalCarbs / 80) * 100, 100)}%`,
                    backgroundColor: glColor,
                  }}
                />
              </div>
              <p
                className="text-[12px] text-[rgba(32,74,58,0.8)] text-center mt-3"
                style={{
                  fontFamily: "'Nunito Sans', sans-serif",
                }}
              >
                {glImpact === "Low"
                  ? "This meal is unlikely to cause a significant glucose spike."
                  : glImpact === "Medium"
                    ? "This meal may cause a moderate glucose increase. Consider pairing with activity."
                    : "This meal may cause a significant glucose spike. Consider reducing carbs."}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Confirm Button */}
      {addedItems.length > 0 && (
        <div className="fixed bottom-0 md:bottom-6 left-0 right-0 md:left-auto md:right-6 max-w-7xl md:max-w-md mx-auto px-4 sm:px-6 pb-4 z-40">
          <button
            onClick={handleConfirmMeal}
            disabled={isSubmitting}
            className="w-full h-[60px] bg-[#1e6177] text-white rounded-full border-none cursor-pointer shadow-[0px_8px_10px_0px_rgba(30,97,119,0.3),0px_20px_25px_0px_rgba(30,97,119,0.3)] text-[18px] disabled:opacity-50 flex items-center justify-center gap-2"
            style={{
              fontFamily: "'Geist', sans-serif",
              fontWeight: 700,
            }}
          >
            {isSubmitting ? (
              <>
                <Loader2 size={24} className="animate-spin" />
                Logging Meal...
              </>
            ) : (
              "Confirm Meal & Predict Glucose"
            )}
          </button>
        </div>
      )}
    </div>
    </ResponsiveLayout>
  );
}
