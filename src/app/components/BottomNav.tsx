import { Home, UtensilsCrossed, User, ClipboardList, Activity } from "lucide-react";
import { useNavigate, useLocation } from "react-router";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/health-check", label: "Health", icon: Activity },
  { path: "/log-meal", label: "Log Meal", icon: UtensilsCrossed },
  { path: "/history", label: "Meal History", icon: ClipboardList },
  { path: "/profile", label: "Profile", icon: User },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="fixed bottom-0 left-0 right-0 backdrop-blur-[12px] bg-[rgba(255,255,255,0.9)] border-t-[0.8px] border-solid border-[rgba(226,234,235,0.5)] h-[80px] z-50 max-w-[430px] mx-auto">
      <div className="flex items-center justify-around h-full px-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className="flex flex-col items-center gap-1 pt-2 cursor-pointer bg-transparent border-none"
            >
              <div className="relative">
                <Icon
                  size={24}
                  className={isActive ? "text-[#1e6177]" : "text-[#637c84]"}
                  fill={isActive ? "#1e6177" : "none"}
                  strokeWidth={1.5}
                />
                {isActive && (
                  <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-[#1e6177]" />
                )}
              </div>
              <p
                className={`text-[11px] tracking-[0.275px] mt-1 ${
                  isActive
                    ? "text-[#1e6177] font-semibold"
                    : "text-[#637c84] font-medium"
                }`}
                style={{ fontFamily: "'Geist', sans-serif" }}
              >
                {item.label}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}