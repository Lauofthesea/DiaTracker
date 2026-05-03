import { Home, UtensilsCrossed, User, ClipboardList, Activity, ChevronLeft, ChevronRight } from "lucide-react";
import { useNavigate, useLocation } from "react-router";
import { useState } from "react";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/health-check", label: "Health Check", icon: Activity },
  { path: "/log-meal", label: "Log Meal", icon: UtensilsCrossed },
  { path: "/history", label: "History", icon: ClipboardList },
  { path: "/profile", label: "Profile", icon: User },
];

interface SideNavProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function SideNav({ collapsed = false, onToggleCollapse }: SideNavProps) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div
      className={`fixed left-0 top-0 h-screen bg-white border-r-[0.8px] border-solid border-[rgba(226,234,235,0.5)] transition-all duration-300 z-50 ${
        collapsed ? "w-[80px]" : "w-[240px]"
      }`}
    >
      {/* Logo/Header */}
      <div className="h-[72px] flex items-center justify-between px-6 border-b-[0.8px] border-solid border-[rgba(226,234,235,0.4)]">
        {!collapsed && (
          <div>
            <h1
              className="text-[18px] text-[#1e6177] tracking-[-0.5px]"
              style={{ fontFamily: "'Geist', sans-serif", fontWeight: 700 }}
            >
              Diabetes Tracker
            </h1>
            <p
              className="text-[11px] text-[#637c84]"
              style={{ fontFamily: "'Nunito Sans', sans-serif" }}
            >
              ML-Powered Health
            </p>
          </div>
        )}
        {collapsed && (
          <div className="w-full flex justify-center">
            <Activity size={28} className="text-[#1e6177]" />
          </div>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="py-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-4 px-6 py-3 cursor-pointer bg-transparent border-none transition-all ${
                isActive
                  ? "bg-[rgba(30,97,119,0.08)] border-l-[3px] border-l-[#1e6177] border-solid"
                  : "border-l-[3px] border-l-transparent"
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                size={24}
                className={isActive ? "text-[#1e6177]" : "text-[#637c84]"}
                strokeWidth={isActive ? 2 : 1.5}
              />
              {!collapsed && (
                <span
                  className={`text-[15px] ${
                    isActive
                      ? "text-[#1e6177] font-semibold"
                      : "text-[#637c84] font-medium"
                  }`}
                  style={{ fontFamily: "'Geist', sans-serif" }}
                >
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Collapse Toggle Button (only on tablet) */}
      {onToggleCollapse && (
        <button
          onClick={onToggleCollapse}
          className="absolute bottom-6 right-[-16px] w-8 h-8 rounded-full bg-white border-[0.8px] border-solid border-[rgba(226,234,235,0.5)] flex items-center justify-center cursor-pointer shadow-sm hover:shadow-md transition-shadow"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight size={16} className="text-[#637c84]" />
          ) : (
            <ChevronLeft size={16} className="text-[#637c84]" />
          )}
        </button>
      )}
    </div>
  );
}
