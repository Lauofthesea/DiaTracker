import { useNavigate } from "react-router";
import { ArrowLeft } from "lucide-react";
import ResponsiveLayout from "./ResponsiveLayout";
import NutritionalSummaryCard from "./analytics/NutritionalSummaryCard";
import TrendChart from "./analytics/TrendChart";

export default function InsightsPage() {
  const navigate = useNavigate();

  return (
    <ResponsiveLayout>
      <div className="bg-[#f4f8f8] min-h-screen w-full mx-auto relative">
        
        <div className="sticky top-0 z-40 backdrop-blur-[12px] bg-[rgba(244,248,248,0.8)] border-b-[0.8px] border-solid border-[rgba(226,234,235,0.4)] px-4 sm:px-6 py-4">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <button onClick={() => navigate("/")} className="bg-[rgba(226,234,235,0.5)] rounded-full w-10 h-10 flex items-center justify-center cursor-pointer border-none md:hidden">
              <ArrowLeft size={24} className="text-[#0d2b35]" />
            </button>
            <p className="text-[20px] text-[#0d2b35] tracking-[-0.5px]" style={{ fontFamily: "'Geist', sans-serif", fontWeight: 600 }}>Insights</p>
          </div>
        </div>

        <div className="px-4 sm:px-6 pt-6 pb-6 max-w-7xl mx-auto">
          
          <div className="mb-4">
            <NutritionalSummaryCard />
          </div>

          
          <div className="mb-4">
            <TrendChart chartType="calories" />
          </div>

          
          <div className="mb-4">
            <TrendChart chartType="macronutrients" />
          </div>
        </div>
      </div>
    </ResponsiveLayout>
  );
}
