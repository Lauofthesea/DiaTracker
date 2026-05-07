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
import { getProfile } from "../../lib/profileApi";
import { getLatestHealthCheck } from "../../lib/healthCheck";
import { predictMealRisk } from "../../lib/mealRiskApi";
import type { FoodSearchResult } from "../../types/food";

type MealType = "breakfast" | "lunch" | "dinner" | "snack";

interface MealItem {
  id: string;
  food_id: string;
  name: string;
  serving: string;
  servingType: "pieces" | "serving"; // Track the serving type
  quantity: number; // Track the quantity
  kcal: number;
  carbs: number;
  fiber: number;
  fat: number;
  protein: number;
  image: string;
  type: MealType;
}

type FoodCategory = "all" | "bakery" | "snacks" | "fruits" | "vegetables" | "protein" | "dairy";

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
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [editQuantity, setEditQuantity] = useState("1");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [mealPrediction, setMealPrediction] = useState<{
    predicted_glucose: number;
    risk_level: string;
    confidence_interval: { lower: number; upper: number };
  } | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const [manualSearchResults, setManualSearchResults] = useState<FoodSearchResult[]>([]);
  const [activeManualEntryIndex, setActiveManualEntryIndex] = useState<number | null>(null);
  const [manualSearchTimer, setManualSearchTimer] = useState<number | null>(null);

  const mealTypes: MealType[] = ["breakfast", "lunch", "dinner", "snack"];
  
  // Map frontend categories to backend categories
  const getCategoryFilter = (category: FoodCategory): string | undefined => {
    switch (category) {
      case "bakery":
        return "Bakery Products";
      case "snacks":
        return "Snacks";
      case "fruits":
        return "Fruits";
      case "vegetables":
        return "Vegetables";
      case "protein":
        return "Protein Foods,Legumes";
      case "dairy":
        return "Dairy,Dairy Alternatives";
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
      console.log('Loading common foods for category:', category, 'filter:', categoryFilter);
      const response = await searchFoods({
        page: 1,
        page_size: 50,
        category: categoryFilter,
      });
      console.log('Common foods response:', response);
      console.log('Number of foods:', response.foods.length);
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

  // Load profile data on mount
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        const profileData = await getProfile();
        setProfile(profileData);
      } catch (err) {
        console.error("Error loading profile:", err);
      }
    };
    loadProfileData();
  }, []);

  // Predict meal glucose when items change
  useEffect(() => {
    // Function to predict meal glucose using RF #1 model
    const predictMealGlucose = async () => {
      if (!profile || addedItems.length === 0) {
        console.log('Skipping prediction:', { hasProfile: !!profile, itemsCount: addedItems.length });
        return;
      }
      
      // Check if profile has required fields
      if (!profile.weight_kg || !profile.height_cm || !profile.age) {
        console.warn('Profile missing required fields for prediction:', profile);
        setError('Please complete your profile (weight, height, age) to see meal predictions.');
        return;
      }
      
      setIsPredicting(true);
      setError(null);
      console.log('Starting meal prediction...', { profile, addedItemsCount: addedItems.length });
      
      try {
        // Calculate total nutrients from added items
        let totalCarbs = 0;
        let totalFat = 0;
        let totalProtein = 0;
        let totalFiber = 0;
        
        // Sum up nutrients from each added item
        for (const item of addedItems) {
          // Ensure values are valid numbers
          const carbs = Number(item.carbs) || 0;
          const fat = Number(item.fat) || 0;
          const protein = Number(item.protein) || 0;
          const fiber = Number(item.fiber) || 0;
          
          totalCarbs += carbs;
          totalFat += fat;
          totalProtein += protein;
          totalFiber += fiber;
        }
        
        // Ensure all values are valid and within acceptable ranges
        totalCarbs = Math.max(0, Math.min(500, totalCarbs));
        totalFat = Math.max(0, Math.min(200, totalFat));
        totalProtein = Math.max(0, Math.min(200, totalProtein));
        totalFiber = Math.max(0, Math.min(100, totalFiber));
        
        console.log('Calculated nutrients:', { totalCarbs, totalFat, totalProtein, totalFiber });
        
        // Get fasting glucose from latest health check or profile
        let fastingGlucose = 100; // Default
        try {
          const latestHealthCheck = await getLatestHealthCheck();
          if (latestHealthCheck?.health_metrics?.blood_sugar_mgdl) {
            fastingGlucose = latestHealthCheck.health_metrics.blood_sugar_mgdl;
          } else if (profile.blood_sugar_mg_dl) {
            fastingGlucose = profile.blood_sugar_mg_dl;
          }
        } catch (err) {
          console.error("Error fetching health check:", err);
          if (profile.blood_sugar_mg_dl) {
            fastingGlucose = profile.blood_sugar_mg_dl;
          }
        }
        
        console.log('Using fasting glucose:', fastingGlucose);
        console.log('Calling predictMealRisk API...');
        
        // Call meal-risk API
        const prediction = await predictMealRisk({
          available_carbs_g: Math.max(0, totalCarbs - totalFiber), // Available carbs = total carbs - fiber
          fat_g: totalFat,
          protein_g: totalProtein,
          fiber_g: totalFiber,
          fasting_glucose: fastingGlucose,
        });
        
        console.log('Prediction received:', prediction);
        
        setMealPrediction({
          predicted_glucose: prediction.predicted_glucose_1hr,
          risk_level: prediction.risk_level,
          confidence_interval: prediction.confidence_interval,
        });
      } catch (err: any) {
        console.error("Error predicting meal glucose:", err);
        console.error("Error details:", err.response?.data || err.message);
        setMealPrediction(null);
        setError(err.response?.data?.detail || 'Failed to predict meal glucose. Please try again.');
      } finally {
        setIsPredicting(false);
      }
    };
    
    if (addedItems.length > 0 && profile) {
      predictMealGlucose();
    } else {
      setMealPrediction(null);
    }
  }, [addedItems, profile]);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, performSearch]);

  const totalCalories = addedItems.reduce((sum, i) => sum + i.kcal, 0);
  const totalCarbs = addedItems.reduce((sum, i) => sum + i.carbs, 0);

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
      
      // Extract nutrients from food details
      let carbs = 0;
      let fiber = 0;
      let fat = 0;
      let protein = 0;
      
      const carbNutrient = foodDetail.nutrients?.find(n => 
        n.name.toLowerCase().includes('carbohydrate')
      );
      if (carbNutrient) {
        carbs = carbNutrient.amount;
      }
      
      const fiberNutrient = foodDetail.nutrients?.find(n => 
        n.name.toLowerCase().includes('fiber')
      );
      if (fiberNutrient) {
        fiber = fiberNutrient.amount;
      }
      
      const fatNutrient = foodDetail.nutrients?.find(n => 
        n.name.toLowerCase().includes('fat')
      );
      if (fatNutrient) {
        fat = fatNutrient.amount;
      }
      
      const proteinNutrient = foodDetail.nutrients?.find(n => 
        n.name.toLowerCase().includes('protein')
      );
      if (proteinNutrient) {
        protein = proteinNutrient.amount;
      }
      
      const quantity = parseFloat(addFoodQuantity) || 1;
      
      // For serving type, quantity is in grams; for pieces, it's the number of pieces
      const servingDesc = addFoodServingType === "pieces" 
        ? `${quantity} pc${quantity > 1 ? 's' : ''}`
        : `${quantity}g`;
      
      // Calculate nutritional values based on serving type
      // Nutritional data is per 100g, so we need to scale accordingly
      const multiplier = addFoodServingType === "pieces" 
        ? quantity  // For pieces, multiply by quantity
        : quantity / 100;  // For grams, divide by 100 to get the multiplier
      
      const item: MealItem = {
        id: `${selectedFoodToAdd.food_id}-${Date.now()}`,
        food_id: selectedFoodToAdd.food_id,
        name: selectedFoodToAdd.name,
        serving: servingDesc,
        servingType: addFoodServingType,
        quantity: quantity,
        kcal: (selectedFoodToAdd.calories_per_serving || 0) * multiplier,
        carbs: carbs * multiplier,
        fiber: fiber * multiplier,
        fat: fat * multiplier,
        protein: protein * multiplier,
        image: "",
        type: addFoodMealType,
      };
      setAddedItems((prev) => [...prev, item]);
      closeAddFoodModal();
    } catch (err) {
      console.error("Error fetching food details:", err);
      const quantity = parseFloat(addFoodQuantity) || 1;
      const servingDesc = addFoodServingType === "pieces" 
        ? `${quantity} pc${quantity > 1 ? 's' : ''}`
        : `${quantity}g`;
      
      const multiplier = addFoodServingType === "pieces" 
        ? quantity
        : quantity / 100;
      
      const item: MealItem = {
        id: `${selectedFoodToAdd.food_id}-${Date.now()}`,
        food_id: selectedFoodToAdd.food_id,
        name: selectedFoodToAdd.name,
        serving: servingDesc,
        servingType: addFoodServingType,
        quantity: quantity,
        kcal: (selectedFoodToAdd.calories_per_serving || 0) * multiplier,
        carbs: 0,
        fiber: 0,
        fat: 0,
        protein: 0,
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

  const startEditingItem = (item: MealItem) => {
    setEditingItemId(item.id);
    setEditQuantity(item.quantity.toString());
  };

  const saveEditedItem = (itemId: string) => {
    const newQuantity = parseFloat(editQuantity) || 1;
    
    setAddedItems((prev) => prev.map((item) => {
      if (item.id !== itemId) return item;
      
      // Recalculate based on new quantity
      const oldMultiplier = item.servingType === "pieces" ? item.quantity : item.quantity / 100;
      const newMultiplier = item.servingType === "pieces" ? newQuantity : newQuantity / 100;
      const ratio = newMultiplier / oldMultiplier;
      
      const servingDesc = item.servingType === "pieces" 
        ? `${newQuantity} pc${newQuantity > 1 ? 's' : ''}`
        : `${newQuantity}g`;
      
      return {
        ...item,
        quantity: newQuantity,
        serving: servingDesc,
        kcal: item.kcal * ratio,
        carbs: item.carbs * ratio,
        fiber: item.fiber * ratio,
        fat: item.fat * ratio,
        protein: item.protein * ratio,
      };
    }));
    
    setEditingItemId(null);
  };

  const cancelEditingItem = () => {
    setEditingItemId(null);
    setEditQuantity("1");
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
      servingType: "serving" as const,
      quantity: 1,
      kcal: parseInt(entry.kcal) || 0,
      carbs: parseInt(entry.carbs) || 0,
      fiber: 0, // Manual entries don't have detailed nutrients
      fat: 0,
      protein: 0,
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
      let firstEntryId: string | null = null;
      
      for (const item of addedItems) {
        try {
          let entryResponse;
          if (item.food_id) {
            // For items with food_id, use the standard API
            entryResponse = await createFoodEntry({
              food_id: item.food_id,
              quantity: 100, // Default quantity
              unit: "g",
              meal_type: item.type,
              consumed_at: timestamp,
            });
            if (!firstEntryId) firstEntryId = entryResponse.entry_id;
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
            entryResponse = await createFoodEntry({
              food_id: customFood.food_id,
              quantity: 100, // 100g standard unit
              unit: "g",
              meal_type: item.type,
              consumed_at: timestamp,
            });
            if (!firstEntryId) firstEntryId = entryResponse.entry_id;
            successCount++;
          }
        } catch (itemError) {
          console.error(`Failed to log ${item.name}:`, itemError);
          failCount++;
        }
      }

      // Save meal prediction with food_entry_id if we have a prediction and successfully created entries
      if (successCount > 0 && mealPrediction && firstEntryId) {
        try {
          // Calculate total nutrients from added items
          let totalCarbs = 0;
          let totalFat = 0;
          let totalProtein = 0;
          let totalFiber = 0;
          
          for (const item of addedItems) {
            const carbs = Number(item.carbs) || 0;
            const kcal = Number(item.kcal) || 0;
            
            totalCarbs += carbs;
            totalFat += kcal * 0.3 / 9;
            totalProtein += kcal * 0.2 / 4;
            totalFiber += carbs * 0.1;
          }
          
          // Get fasting glucose
          let fastingGlucose = 100;
          try {
            const latestHealthCheck = await getLatestHealthCheck();
            if (latestHealthCheck?.health_metrics?.blood_sugar_mgdl) {
              fastingGlucose = latestHealthCheck.health_metrics.blood_sugar_mgdl;
            } else if (profile?.blood_sugar_mg_dl) {
              fastingGlucose = profile.blood_sugar_mg_dl;
            }
          } catch (err) {
            if (profile?.blood_sugar_mg_dl) {
              fastingGlucose = profile.blood_sugar_mg_dl;
            }
          }
          
          // Save prediction with food_entry_id
          await predictMealRisk({
            available_carbs_g: Math.max(0, Math.min(500, totalCarbs - totalFiber)), // Available carbs = total carbs - fiber
            fat_g: Math.max(0, Math.min(200, totalFat)),
            protein_g: Math.max(0, Math.min(200, totalProtein)),
            fiber_g: Math.max(0, Math.min(100, totalFiber)),
            fasting_glucose: fastingGlucose,
            food_entry_id: firstEntryId, // Link to first food entry
          });
        } catch (predError) {
          console.error("Failed to save meal prediction:", predError);
          // Don't fail the whole operation if prediction fails
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
                  className="bg-white border-[0.8px] border-[rgba(226,234,235,0.3)] rounded-2xl shadow-sm p-3"
                >
                  {editingItemId === item.id ? (
                    // Edit mode
                    <div className="space-y-3">
                      <p className="text-[14px] text-[#0d2b35] font-semibold" style={{ fontFamily: "'Geist', sans-serif" }}>
                        Edit {item.name}
                      </p>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          min="0.1"
                          step={item.servingType === "pieces" ? "1" : "10"}
                          value={editQuantity}
                          onChange={(e) => setEditQuantity(e.target.value)}
                          className="flex-1 h-[40px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-3 text-[14px] outline-none"
                        />
                        <span className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                          {item.servingType === "pieces" ? "pcs" : "g"}
                        </span>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => saveEditedItem(item.id)}
                          className="flex-1 h-[36px] bg-[#1e6177] text-white rounded-xl border-none cursor-pointer text-[14px]"
                          style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
                        >
                          Save
                        </button>
                        <button
                          onClick={cancelEditingItem}
                          className="flex-1 h-[36px] bg-gray-200 text-gray-700 rounded-xl border-none cursor-pointer text-[14px]"
                          style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View mode
                    <div className="flex items-center gap-3">
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
                          {Math.round(item.kcal)}{" "}
                          <span className="text-[10px] text-[#637c84] uppercase">kcal</span>
                        </p>
                        <p
                          className="text-[10px] text-[#8aab9f] uppercase"
                          style={{
                            fontFamily: "'Nunito Sans', sans-serif",
                            fontWeight: 700,
                          }}
                        >
                          {Math.round(item.carbs)}g Carbs
                        </p>
                      </div>
                      <button
                        onClick={() => startEditingItem(item)}
                        className="bg-[rgba(30,97,119,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0"
                      >
                        <PenLine size={16} className="text-[#1e6177]" />
                      </button>
                      <button
                        onClick={() => removeItem(item.id)}
                        className="bg-[rgba(239,68,68,0.1)] w-8 h-8 rounded-full flex items-center justify-center border-none cursor-pointer shrink-0"
                      >
                        <Minus size={16} className="text-[#ef4444]" />
                      </button>
                    </div>
                  )}
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
              Meal Summary & Prediction
            </p>
            
            {/* Nutritional Summary */}
            <div className="flex justify-between mb-4">
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
                  {Math.round(totalCalories)}
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
                  {Math.round(totalCarbs)}
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
                  Items
                </p>
                <p
                  className="text-[24px] text-[#204a3a]"
                  style={{
                    fontFamily: "'Geist', sans-serif",
                    fontWeight: 700,
                  }}
                >
                  {addedItems.length}
                </p>
              </div>
            </div>

            {/* Glucose Prediction from RF #1 */}
            {isPredicting ? (
              <div className="bg-[rgba(255,255,255,0.6)] rounded-2xl p-4 flex items-center justify-center gap-2">
                <Loader2 size={20} className="text-[#1e6177] animate-spin" />
                <p className="text-[14px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  Analyzing meal impact...
                </p>
              </div>
            ) : mealPrediction ? (
              <div className="bg-[rgba(255,255,255,0.6)] rounded-2xl p-4">
                <div className="flex justify-between items-center mb-3">
                  <p
                    className="text-[12px] text-[#637c84] tracking-[0.6px] uppercase"
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    Predicted 1-Hour Glucose
                  </p>
                  <div className="flex items-center gap-2">
                    <div
                      className={`px-3 py-1 rounded-full text-[10px] uppercase tracking-[0.5px] ${
                        mealPrediction.risk_level === 'Low'
                          ? 'bg-[rgba(138,171,159,0.2)] text-[#204a3a]'
                          : mealPrediction.risk_level === 'Mid'
                            ? 'bg-[rgba(245,158,11,0.2)] text-[#92400e]'
                            : 'bg-[rgba(239,68,68,0.2)] text-[#991b1b]'
                      }`}
                      style={{
                        fontFamily: "'Nunito Sans', sans-serif",
                        fontWeight: 700,
                      }}
                    >
                      {mealPrediction.risk_level} Risk
                    </div>
                  </div>
                </div>
                
                <div className="flex items-baseline gap-2 mb-2">
                  <p
                    className="text-[36px] text-[#204a3a]"
                    style={{
                      fontFamily: "'Geist', sans-serif",
                      fontWeight: 700,
                    }}
                  >
                    {Math.round(mealPrediction.predicted_glucose)}
                  </p>
                  <p
                    className="text-[14px] text-[rgba(32,74,58,0.6)]"
                    style={{
                      fontFamily: "'Nunito Sans', sans-serif",
                      fontWeight: 600,
                    }}
                  >
                    mg/dL
                  </p>
                </div>
                
                <p
                  className="text-[11px] text-[rgba(32,74,58,0.7)] mb-3"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                  }}
                >
                  Confidence: {Math.round(mealPrediction.confidence_interval.lower)} - {Math.round(mealPrediction.confidence_interval.upper)} mg/dL
                </p>
                
                <div className="bg-[rgba(226,234,235,0.3)] h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.min((mealPrediction.predicted_glucose / 200) * 100, 100)}%`,
                      backgroundColor: 
                        mealPrediction.risk_level === 'Low' ? '#8aab9f' :
                        mealPrediction.risk_level === 'Mid' ? '#f59e0b' : '#ef4444',
                    }}
                  />
                </div>
                
                <p
                  className="text-[12px] text-[rgba(32,74,58,0.8)] text-center mt-3"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                  }}
                >
                  {mealPrediction.risk_level === 'Low'
                    ? "This meal is unlikely to cause a significant glucose spike."
                    : mealPrediction.risk_level === 'Mid'
                      ? "This meal may cause a moderate glucose increase. Consider pairing with activity."
                      : "This meal may cause a significant glucose spike. Consider reducing portions."}
                </p>
                
                <p
                  className="text-[10px] text-[rgba(32,74,58,0.5)] text-center mt-2"
                  style={{
                    fontFamily: "'Nunito Sans', sans-serif",
                    fontStyle: 'italic',
                  }}
                >
                  Powered by RF #1 Glucose Predictor
                </p>
              </div>
            ) : (
              <div className="bg-[rgba(255,255,255,0.6)] rounded-2xl p-4">
                <p className="text-[12px] text-[#637c84] text-center" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                  Add items to see glucose prediction
                </p>
              </div>
            )}
          </div>
        )}

        
        {showManualEntry && (
          <div
            className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4"
            onClick={() => setShowManualEntry(false)}
          >
            <div
              className="bg-white rounded-3xl w-full max-w-[430px] p-6 pb-24 max-h-[90vh] overflow-y-auto"
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
                      <div className="relative">
                        <input
                          placeholder="Search food name..."
                          value={entry.name}
                          onChange={(e) => {
                            const value = e.target.value;
                            updateManualEntry(index, "name", value);
                            setActiveManualEntryIndex(index);
                            
                            // Clear previous timer
                            if (manualSearchTimer) {
                              clearTimeout(manualSearchTimer);
                            }
                            
                            // Trigger search after 300ms delay
                            if (value.length >= 2) {
                              const timer = setTimeout(async () => {
                                try {
                                  console.log('Searching for:', value);
                                  const response = await searchFoods({
                                    q: value,
                                    page: 1,
                                    page_size: 10,
                                  });
                                  console.log('Search results:', response.foods);
                                  // Ensure we have an array of foods
                                  if (Array.isArray(response.foods)) {
                                    setManualSearchResults(response.foods);
                                  } else {
                                    console.error('Invalid response format:', response);
                                    setManualSearchResults([]);
                                  }
                                } catch (err: any) {
                                  console.error("Manual search error:", err);
                                  console.error("Error response:", err.response?.data);
                                  setManualSearchResults([]);
                                }
                              }, 300);
                              setManualSearchTimer(timer);
                            } else {
                              setManualSearchResults([]);
                            }
                          }}
                          onFocus={() => setActiveManualEntryIndex(index)}
                          className="h-[48px] w-full rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                        />
                        {/* Show dropdown if there are search results and this field is active */}
                        {activeManualEntryIndex === index && entry.name.length >= 2 && manualSearchResults.length > 0 && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-white border-[0.8px] border-[rgba(226,234,235,0.4)] rounded-xl shadow-lg max-h-[200px] overflow-y-auto z-10">
                            {manualSearchResults.map((food) => (
                              <button
                                key={food.food_id}
                                onClick={() => {
                                  // When user selects a food, add it directly
                                  openAddFoodModal(food);
                                  setShowManualEntry(false);
                                  setManualSearchResults([]);
                                  setActiveManualEntryIndex(null);
                                }}
                                className="w-full text-left px-4 py-3 hover:bg-[rgba(226,234,235,0.2)] border-none bg-transparent cursor-pointer flex items-center justify-between"
                              >
                                <div className="flex-1">
                                  <p className="text-[14px] text-[#0d2b35]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>
                                    {food.name}
                                  </p>
                                  <p className="text-[12px] text-[#637c84]" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                                    {food.category}
                                  </p>
                                </div>
                                <p className="text-[12px] text-[#637c84]">
                                  {food.calories_per_serving ? `${Math.round(food.calories_per_serving)} kcal` : ''}
                                </p>
                              </button>
                            ))}
                          </div>
                        )}
                        {/* Show "No results" message */}
                        {activeManualEntryIndex === index && entry.name.length >= 2 && manualSearchResults.length === 0 && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-white border-[0.8px] border-[rgba(226,234,235,0.4)] rounded-xl shadow-lg p-4 z-10">
                            <p className="text-[14px] text-[#637c84] text-center" style={{ fontFamily: "'Nunito Sans', sans-serif" }}>
                              No foods found. Try a different search term.
                            </p>
                          </div>
                        )}
                      </div>
                      <input
                        placeholder={servingSizeType === "amount" ? "Amount (e.g. 2 pcs)" : "Serving size (e.g. 250g)"}
                        value={entry.serving}
                        onChange={(e) => updateManualEntry(index, "serving", e.target.value)}
                        className="h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                      />
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
            className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4"
            onClick={closeAddFoodModal}
          >
            <div
              className="bg-white rounded-3xl w-full max-w-[430px] p-6 max-h-[90vh] overflow-y-auto"
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
                    Serving
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
                  {addFoodServingType === "pieces" ? "Number of Pieces" : "Serving Size (grams)"}
                </p>
                <input
                  type="number"
                  min="1"
                  step={addFoodServingType === "pieces" ? "1" : "10"}
                  value={addFoodQuantity}
                  onChange={(e) => setAddFoodQuantity(e.target.value)}
                  placeholder={addFoodServingType === "pieces" ? "e.g., 2" : "e.g., 150"}
                  className="w-full h-[48px] rounded-xl bg-[rgba(226,234,235,0.2)] border-[0.8px] border-[rgba(226,234,235,0.4)] px-4 text-[14px] outline-none"
                />
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
              onClick={() => setSelectedCategory("bakery")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "bakery"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Bakery
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
              onClick={() => setSelectedCategory("fruits")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "fruits"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Fruits
            </button>
            <button
              onClick={() => setSelectedCategory("vegetables")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "vegetables"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Vegetables
            </button>
            <button
              onClick={() => setSelectedCategory("protein")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "protein"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Protein
            </button>
            <button
              onClick={() => setSelectedCategory("dairy")}
              className={`h-[38px] px-4 rounded-full border-[0.8px] cursor-pointer text-[14px] ${
                selectedCategory === "dairy"
                  ? "bg-[#1e6177] border-[#1e6177] text-white"
                  : "bg-white border-[#e2eaeb] text-[#637c84]"
              }`}
              style={{
                fontFamily: "'Nunito Sans', sans-serif",
                fontWeight: 500,
              }}
            >
              Dairy
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
               selectedCategory === "bakery" ? "Bakery Products" :
               selectedCategory === "snacks" ? "Snacks" :
               selectedCategory === "fruits" ? "Fruits" :
               selectedCategory === "vegetables" ? "Vegetables" :
               selectedCategory === "protein" ? "Protein Foods" : "Dairy Products"}
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
        <div className="fixed bottom-[100px] md:bottom-8 left-0 right-0 px-4 sm:px-6 z-40">
          <div className="max-w-7xl mx-auto flex justify-center md:justify-end">
            <button
              onClick={handleConfirmMeal}
              disabled={isSubmitting}
              className="w-full md:w-auto md:min-w-[280px] h-[68px] bg-[#1e6177] text-white rounded-full border-none cursor-pointer shadow-[0px_8px_10px_0px_rgba(30,97,119,0.3),0px_20px_25px_0px_rgba(30,97,119,0.3)] text-[17px] disabled:opacity-50 flex items-center justify-center gap-2 hover:bg-[#1a5565] transition-colors px-8"
              style={{
                fontFamily: "'Geist', sans-serif",
                fontWeight: 800,
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
        </div>
      )}
    </div>
    </ResponsiveLayout>
  );
}
