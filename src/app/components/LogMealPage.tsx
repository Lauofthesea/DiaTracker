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
import { searchFoods, createFoodEntry, createCustomFood, getFoodDetail } from "../../lib/foodApi";
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

type FoodCategory = "all" | "viands" | "snacks" | "desserts";

export default function LogMealPage() {
  const navigate = useNavigate();
  const [selectedType, setSelectedType] = useState<MealType>("breakfast");
  const [selectedCategory, setSelectedCategory] = useState<FoodCategory>("all");
  const [addedItems, setAddedItems] = useState<MealItem[]>([]);
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualMealType, setManualMealType] = useState<MealType>("breakfast");
  const [servingSizeType, setServingSizeType] = useState<"amount" | "serving">("serving");
  const [manualEntries, setManualEntries] = useState<Array<{
    name: string;
    serving: string;
    kcal: string;
    carbs: string;
  }>>([{ name: "", serving: "", kcal: "", carbs: "" }]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<FoodSearchResult[]>([]);
  const [commonFoods, setCommonFoods] = useState<FoodSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingCommon, setIsLoadingCommon] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAddingFood, setIsAddingFood] = useState<string | null>(null); // Track which food is being added
  const [showAddFoodModal, setShowAddFoodModal] = useState(false);
  const [selectedFoodToAdd, setSelectedFoodToAdd] = useState<FoodSearchResult | null>(null);
  const [addFoodMealType, setAddFoodMealType] = useState<MealType>("breakfast");
  const [addFoodServingType, setAddFoodServingType] = useState<"pieces" | "serving">("serving");
  const [addFoodQuantity, setAddFoodQuantity] = useState("1");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const mealTypes: MealType[] = ["breakfast", "lunch", "dinner", "snack"];
  
  // Map frontend categories to backend categories
  const getCategoryFilter = (category: FoodCategory): string | undefined => {
    switch (category) {
      case "viands":
        return "Main Dish,Soup,Seafood,Noodles";
      case "snacks":
        return "Snack,Appetizer,Porridge";
      case "desserts":
        return "Dessert";
      case "all":
      default:
        return undefined;
    }
  };

  // Load common foods based on category
  const loadCommonFoods = useCallback(async (category: FoodCategory) => {
    setIsLoadingCommon(true);
    setError(null);

    try {
      const categoryFilter = getCategoryFilter(category);
      const response = await searchFoods({
        page: 1,
        page_size: 50,
        category: categoryFilter,
      });
      setCommonFoods(response.foods);
    } catch (err) {
      console.error("Error loading common foods:", err);
      setError(err instanceof Error ? err.message : "Failed to load foods");
      setCommonFoods([]);
    } finally {
      setIsLoadingCommon(false);
    }
  }, []);

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
      console.log('Search response:', response);
      console.log('First food:', response.foods[0]);
      setSearchResults(response.foods);
    } catch (err) {
      console.error("Search error:", err);
      setError(err instanceof Error ? err.message : "Failed to search foods");
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  // Load common foods on mount and when category changes
  useEffect(() => {
    loadCommonFoods(selectedCategory);
  }, [selectedCategory, loadCommonFoods]);

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

  const openAddFoodModal = (food: FoodSearchResult) => {
    setSelectedFoodToAdd(food);
    setAddFoodMealType(selectedType); // Default to currently selected meal type
    setAddFoodServingType("serving");
    setAddFoodQuantity("1");
    setShowAddFoodModal(true);
  };

  const closeAddFoodModal = () => {
    setShowAddFoodModal(false);
    setSelectedFoodToAdd(null);
    setAddFoodMealType("breakfast");
    setAddFoodServingType("serving");
    setAddFoodQuantity("1");
  };

  const confirmAddFood = async () => {
    if (!selectedFoodToAdd) return;
    
    setIsAddingFood(selectedFoodToAdd.food_id);
    try {
      // Fetch detailed nutritional information
      const foodDetail = await getFoodDetail(selectedFoodToAdd.food_id);
      
      // Extract carbs from nutrients
      let carbs = 0;
      const carbNutrient = foodDetail.nutrients?.find(n => 
        n.name.toLowerCase().includes('carbohydrate')
      );
      if (carbNutrient) {
        carbs = carbNutrient.amount;
      }
      
      // Calculate serving description
      const quantity = parseFloat(addFoodQuantity) || 1;
      const servingDesc = addFoodServingType === "pieces" 
        ? `${quantity} pc${quantity > 1 ? 's' : ''}`
        : `${quantity * 100}g`;
      
      const item: MealItem = {
        id: `${selectedFoodToAdd.food_id}-${Date.now()}`,
        food_id: selectedFoodToAdd.food_id,
        name: selectedFoodToAdd.name,
        serving: servingDesc,
        kcal: (selectedFoodToAdd.calories_per_serving || 0) * quantity,
        carbs: carbs * quantity,
        image: "",
        type: addFoodMealType,
      };
      setAddedItems((prev) => [...prev, item]);
      closeAddFoodModal();
    } catch (err) {
      console.error("Error fetching food details:", err);
      // Fallback: add without carbs
      const quantity = parseFloat(addFoodQuantity) || 1;
      const servingDesc = addFoodServingType === "pieces" 
        ? `${quantity} pc${quantity > 1 ? 's' : ''}`
        : `${quantity * 100}g`;
      
      const item: MealItem = {
        id: `${selectedFoodToAdd.food_id}-${Date.now()}`,
        food_id: selectedFoodToAdd.food_id,
        name: selectedFoodToAdd.name,
        serving: servingDesc,
        kcal: (selectedFoodToAdd.calories_per_serving || 0) * quantity,
        carbs: 0,
        image: "",
        type: addFoodMealType,
      };
      setAddedItems((prev) => [...prev, item]);
      closeAddFoodModal();
    } finally {
      setIsAddingFood(null);
    }
  };

  const addFoodItem = async (food: FoodSearchResult) => {
    // Open modal instead of adding directly
    openAddFoodModal(food);
  };

  const removeItem = (id: string) => {
    setAddedItems((prev) => prev.filter((i) => i.id !== id));
  };

  const addManualEntryField = () => {
    setManualEntries([...manualEntries, { name: "", serving: "", kcal: "", carbs: "" }]);
  };

  const removeManualEntryField = (index: number) => {
    if (manualEntries.length > 1) {
      setManualEntries(manualEntries.filter((_, i) => i !== index));
    }
  };

  const updateManualEntry = (index: number, field: string, value: string) => {
    const updated = [...manualEntries];
    updated[index] = { ...updated[index], [field]: value };
    setManualEntries(updated);
  };

  const submitManual = () => {
    // Validate at least one entry has name and kcal
    const validEntries = manualEntries.filter(entry => entry.name && entry.kcal);
    if (validEntries.length === 0) return;

    // Add all valid entries to the meal
    const newItems = validEntries.map((entry, idx) => ({
      id: `manual-${Date.now()}-${idx}`,
      food_id: "", // Manual entries don't have a food_id
      name: entry.name,
      serving: entry.serving || "1 serving",
      kcal: parseInt(entry.kcal) || 0,
      carbs: parseInt(entry.carbs) || 0,
      image: "",
      type: manualMealType,
    }));

    setAddedItems((prev) => [...prev, ...newItems]);
    
    // Reset modal state
    setManualEntries([{ name: "", serving: "", kcal: "", carbs: "" }]);
    setManualMealType("breakfast");
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
      let successCount = 0;
      let failCount = 0;
      
      for (const item of addedItems) {
        try {
          if (item.food_id) {
            // For items with food_id, use the standard API
            await createFoodEntry({
              food_id: item.food_id,
              quantity: 100, // Default quantity
              unit: "g",
              meal_type: item.type,
              consumed_at: timestamp,
            });
            successCount++;
          } else {
            // For manual entries, create custom food first, then create entry
            const customFood = await createCustomFood({
              name: item.name,
              serving_size: item.serving,
              calories: item.kcal,
              carbohydrates_g: item.carbs || 0,
            });
            
            // Now create food entry with the custom food_id
            await createFoodEntry({
              food_id: customFood.food_id,
              quantity: 100, // 100g standard unit
              unit: "g",
              meal_type: item.type,
              consumed_at: timestamp,
            });
            successCount++;
          }
        } catch (itemError) {
          console.error(`Failed to log ${item.name}:`, itemError);
          failCount++;
        }
      }

      if (successCount > 0) {
        setSuccessMessage(
          failCount > 0 
            ? `${successCount} item(s) logged. ${failCount} failed.`
            : "Meal logged successfully!"
        );
        setAddedItems([]);
        
        // Navigate to home and force reload
        setTimeout(() => {
          navigate("/");
          window.location.reload(); // Force page reload to update glucose tracker
        }, 1500);
      } else {
        setError("Failed to log meal. Please try again.");
      }
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

        <div className="px-4 sm:px-6 pb-[160px] md:pb-6 pt-4 overflow-auto max-w-7xl mx-auto">
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

        
        {showManualEntry && (
          <div
            className="fixed inset-0 bg-black/30 z-50 flex items-end justify-center"
            onClick={() => setShowManualEntry(false)}
          >
            <div
              className="bg-white rounded-t-3xl w-full max-w-[430px] p-6 max-h-[85vh] overflow-y-auto"
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
                  onClick={() => {
                    setShowManualEntry(false);
                    setManualEntries([{ name: "", serving: "", kcal: "", carbs: "" }]);
                    setManualMealType("breakfast");
                    setServingSizeType("serving");
                  }}
                  className="bg-transparent border-none cursor-pointer"
                >
                  <X size={24} className="text-[#637c84]" />
                </button>
              </div>

              
              <div className="mb-5">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Meal Type
                </p>
                <div className="flex gap-2 flex-wrap">
                  {mealTypes.map((type) => (
                    <button
                      key={type}
                      onClick={() => setManualMealType(type)}
                      className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] capitalize ${
                        manualMealType === type
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

              
              <div className="mb-5">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Serving Type
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setServingSizeType("amount")}
                    className={`flex-1 h-[48px] rounded-2xl border-[0.8px] cursor-pointer text-[14px] ${
                      servingSizeType === "amount"
                        ? "bg-[#1e6177] border-[#1e6177] text-white"
                        : "bg-white border-[#e2eaeb] text-[#637c84]"
                    }`}
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    Amount (pcs)
                  </button>
                  <button
                    onClick={() => setServingSizeType("serving")}
                    className={`flex-1 h-[48px] rounded-2xl border-[0.8px] cursor-pointer text-[14px] ${
                      servingSizeType === "serving"
                        ? "bg-[#1e6177] border-[#1e6177] text-white"
                        : "bg-white border-[#e2eaeb] text-[#637c84]"
                    }`}
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    Serving Size
                  </button>
                </div>
              </div>

              
              <div className="flex flex-col gap-4">
                {manualEntries.map((entry, index) => (
                  <div key={index} className="border-[0.8px] border-[rgba(226,234,235,0.4)] rounded-2xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <p
                        className="text-[14px] text-[#0d2b35]"
                        style={{
                          fontFamily: "'Geist', sans-serif",
                          fontWeight: 600,
                        }}
                      >
                        Food Item {index + 1}
                      </p>
                      {manualEntries.length > 1 && (
                        <button
                          onClick={() => removeManualEntryField(index)}
                          className="bg-[rgba(239,68,68,0.1)] w-7 h-7 rounded-full flex items-center justify-center border-none cursor-pointer"
                        >
                          <X size={14} className="text-[#ef4444]" />
                        </button>
                      )}
                    </div>
                    <div className="flex flex-col gap-3">
                      <input
                        placeholder="Food name *"
                        value={entry.name}
                        onChange={(e) => updateManualEntry(index, "name", e.target.value)}
                        className="h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                      />
                      <input
                        placeholder={servingSizeType === "amount" ? "Amount (e.g. 2 pcs)" : "Serving size (e.g. 250g)"}
                        value={entry.serving}
                        onChange={(e) => updateManualEntry(index, "serving", e.target.value)}
                        className="h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                      />
                      <div className="flex gap-3">
                        <input
                          placeholder="Calories (kcal) *"
                          type="number"
                          value={entry.kcal}
                          onChange={(e) => updateManualEntry(index, "kcal", e.target.value)}
                          className="flex-1 h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                        />
                        <input
                          placeholder="Carbs (g)"
                          type="number"
                          value={entry.carbs}
                          onChange={(e) => updateManualEntry(index, "carbs", e.target.value)}
                          className="flex-1 h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                        />
                      </div>
                    </div>
                  </div>
                ))}

                
                <button
                  onClick={addManualEntryField}
                  className="h-[48px] bg-[rgba(30,97,119,0.1)] text-[#1e6177] rounded-2xl border-[0.8px] border-[rgba(30,97,119,0.2)] cursor-pointer text-[14px] flex items-center justify-center gap-2"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  <Plus size={18} />
                  Add More Food
                </button>

                
                <button
                  onClick={submitManual}
                  disabled={!manualEntries.some(e => e.name && e.kcal)}
                  className="h-[52px] bg-[#1e6177] text-white rounded-2xl border-none cursor-pointer text-[16px] disabled:opacity-50"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 600,
                  }}
                >
                  Add {manualEntries.filter(e => e.name && e.kcal).length} Item(s) to {manualMealType.charAt(0).toUpperCase() + manualMealType.slice(1)}
                </button>
              </div>
            </div>
          </div>
        )}

        
        {showAddFoodModal && selectedFoodToAdd && (
          <div
            className="fixed inset-0 bg-black/30 z-50 flex items-end justify-center"
            onClick={closeAddFoodModal}
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
                  Add {selectedFoodToAdd.name}
                </p>
                <button
                  onClick={closeAddFoodModal}
                  className="bg-transparent border-none cursor-pointer"
                >
                  <X size={24} className="text-[#637c84]" />
                </button>
              </div>

              
              <div className="mb-5">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Meal Type
                </p>
                <div className="flex gap-2 flex-wrap">
                  {mealTypes.map((type) => (
                    <button
                      key={type}
                      onClick={() => setAddFoodMealType(type)}
                      className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] capitalize ${
                        addFoodMealType === type
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

              
              <div className="mb-5">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Serving Type
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setAddFoodServingType("pieces")}
                    className={`flex-1 h-[48px] rounded-2xl border-[0.8px] cursor-pointer text-[14px] ${
                      addFoodServingType === "pieces"
                        ? "bg-[#1e6177] border-[#1e6177] text-white"
                        : "bg-white border-[#e2eaeb] text-[#637c84]"
                    }`}
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    Pieces
                  </button>
                  <button
                    onClick={() => setAddFoodServingType("serving")}
                    className={`flex-1 h-[48px] rounded-2xl border-[0.8px] cursor-pointer text-[14px] ${
                      addFoodServingType === "serving"
                        ? "bg-[#1e6177] border-[#1e6177] text-white"
                        : "bg-white border-[#e2eaeb] text-[#637c84]"
                    }`}
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    Serving (100g)
                  </button>
                </div>
              </div>

              
              <div className="mb-5">
                <p
                  className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Quantity
                </p>
                <input
                  type="number"
                  min="0.1"
                  step="0.1"
                  value={addFoodQuantity}
                  onChange={(e) => setAddFoodQuantity(e.target.value)}
                  placeholder={addFoodServingType === "pieces" ? "Number of pieces" : "Number of servings"}
                  className="w-full h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                />
                <p className="text-[12px] text-[#637c84] mt-2">
                  {addFoodServingType === "pieces" 
                    ? `${addFoodQuantity} piece${parseFloat(addFoodQuantity) !== 1 ? 's' : ''}`
                    : `${parseFloat(addFoodQuantity) * 100}g (${addFoodQuantity} serving${parseFloat(addFoodQuantity) !== 1 ? 's' : ''})`
                  }
                </p>
              </div>

              
              <button
                onClick={confirmAddFood}
                disabled={isAddingFood !== null}
                className="w-full h-[52px] bg-[#1e6177] text-white rounded-2xl border-none cursor-pointer text-[16px] disabled:opacity-50 flex items-center justify-center gap-2"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                {isAddingFood ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Adding...
                  </>
                ) : (
                  `Add to ${addFoodMealType.charAt(0).toUpperCase() + addFoodMealType.slice(1)}`
                )}
              </button>
            </div>
          </div>
        )}

        
        <div className="mb-4">
          <p
            className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
            style={{
              fontFamily: "'Geist', sans-serif",
              fontWeight: 700,
            }}
          >
            Common Foods
          </p>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedCategory("all")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "all"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              All
            </button>
            <button
              onClick={() => setSelectedCategory("viands")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "viands"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Viands
            </button>
            <button
              onClick={() => setSelectedCategory("snacks")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "snacks"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Snacks
            </button>
            <button
              onClick={() => setSelectedCategory("desserts")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "desserts"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Desserts
            </button>
          </div>
        </div>

        
        {!searchQuery && commonFoods.length > 0 && (
          <div className="mb-4">
            <p
              className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase mb-3"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 700,
              }}
            >
              {selectedCategory === "all" ? "All Foods" : 
               selectedCategory === "viands" ? "Viands" :
               selectedCategory === "snacks" ? "Snacks" : "Desserts"}
            </p>
            {isLoadingCommon ? (
              <div className="flex justify-center py-8">
                <Loader2 size={32} className="text-[#1e6177] animate-spin" />
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {commonFoods.map((food) => (
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
                        {food.calories_per_serving != null 
                          ? Math.round(Number(food.calories_per_serving))
                          : "N/A"}{" "}
                        <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                      </p>
                    </div>
                    <button
                      onClick={() => addFoodItem(food)}
                      disabled={isAddingFood === food.food_id}
                      className="bg-[rgba(30,97,119,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0 disabled:opacity-50"
                    >
                      {isAddingFood === food.food_id ? (
                        <Loader2 size={16} className="text-[#1e6177] animate-spin" />
                      ) : (
                        <Plus size={16} className="text-[#1e6177]" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        
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
                      {food.calories_per_serving != null 
                        ? Math.round(Number(food.calories_per_serving))
                        : "N/A"}{" "}
                      <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                    </p>
                  </div>
                  <button
                    onClick={() => addFoodItem(food)}
                    disabled={isAddingFood === food.food_id}
                    className="bg-[rgba(30,97,119,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0 disabled:opacity-50"
                  >
                    {isAddingFood === food.food_id ? (
                      <Loader2 size={16} className="text-[#1e6177] animate-spin" />
                    ) : (
                      <Plus size={16} className="text-[#1e6177]" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      
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
              "Confirm Meal"
            )}
          </button>
        </div>
      )}
    </div>
    </ResponsiveLayout>
  );
}
