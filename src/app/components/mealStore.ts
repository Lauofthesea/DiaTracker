/**
 * @deprecated This localStorage-based meal store is deprecated.
 * Use the API-based food entry system instead (see src/lib/foodApi.ts).
 * This file is kept for backward compatibility only.
 */

export interface MealHistoryEntry {
  id: string;
  name: string;
  serving: string;
  kcal: number;
  carbs: number;
  image: string;
  type: "Breakfast" | "Lunch" | "Dinner" | "Snack";
  date: string; // ISO string
}

const STORAGE_KEY = "meal_history";

function generatePastEntries(): MealHistoryEntry[] {
  const now = new Date();
  const entries: MealHistoryEntry[] = [
    // Today
    { id: "h1", name: "Oatmeal Bowl", serving: "250g bowl", kcal: 280, carbs: 48, image: "", type: "Breakfast", date: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 7, 30).toISOString() },
    { id: "h2", name: "Grilled Chicken Salad", serving: "300g bowl", kcal: 350, carbs: 12, image: "", type: "Lunch", date: new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12, 15).toISOString() },
    // Yesterday
    { id: "h3", name: "Scrambled Eggs & Toast", serving: "2 eggs, 1 slice", kcal: 310, carbs: 18, image: "", type: "Breakfast", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 8, 0).toISOString() },
    { id: "h4", name: "Turkey Sandwich", serving: "1 sandwich", kcal: 380, carbs: 34, image: "", type: "Lunch", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 13, 0).toISOString() },
    { id: "h5", name: "Grilled Salmon", serving: "200g fillet", kcal: 380, carbs: 4, image: "", type: "Dinner", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 19, 30).toISOString() },
    { id: "h6", name: "Mixed Nuts", serving: "30g handful", kcal: 170, carbs: 6, image: "", type: "Snack", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 16, 0).toISOString() },
    // 2 days ago
    { id: "h7", name: "Greek Yogurt & Granola", serving: "200g cup", kcal: 220, carbs: 28, image: "", type: "Breakfast", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 7, 45).toISOString() },
    { id: "h8", name: "Rice & Veggie Bowl", serving: "350g bowl", kcal: 410, carbs: 58, image: "", type: "Lunch", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 12, 30).toISOString() },
    { id: "h9", name: "Pasta Marinara", serving: "250g plate", kcal: 450, carbs: 65, image: "", type: "Dinner", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 19, 0).toISOString() },
    { id: "h10", name: "Protein Bar", serving: "1 bar (60g)", kcal: 210, carbs: 22, image: "", type: "Snack", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 2, 15, 30).toISOString() },
    // 3 days ago
    { id: "h11", name: "Pancakes with Syrup", serving: "3 pieces", kcal: 420, carbs: 62, image: "", type: "Breakfast", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 3, 8, 15).toISOString() },
    { id: "h12", name: "Tomato Soup & Bread", serving: "1 bowl + 1 slice", kcal: 260, carbs: 38, image: "", type: "Lunch", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 3, 12, 45).toISOString() },
    { id: "h13", name: "Steak & Vegetables", serving: "250g serving", kcal: 520, carbs: 15, image: "", type: "Dinner", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 3, 20, 0).toISOString() },
    { id: "h14", name: "Apple & Peanut Butter", serving: "1 apple + 2 tbsp", kcal: 280, carbs: 30, image: "", type: "Snack", date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 3, 10, 30).toISOString() },
  ];
  return entries;
}

export function getMealHistory(): MealHistoryEntry[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      if (parsed.length > 0) return parsed;
    }
  } catch {}
  const defaults = generatePastEntries();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(defaults));
  return defaults;
}

export function addMealsToHistory(meals: Omit<MealHistoryEntry, "date">[]): void {
  const history = getMealHistory();
  const now = new Date().toISOString();
  const newEntries = meals.map((m) => ({ ...m, date: now }));
  const updated = [...newEntries, ...history];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}
