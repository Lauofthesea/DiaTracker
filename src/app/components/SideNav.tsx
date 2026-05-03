import { Home, UtensilsCrossed, User, ClipboardList, Activity, ChevronLeft, ChevronRight, LogOut, Loader2 } from "lucide-react";
import { useNavigate, useLocation } from "react-router";
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/health-check", label: "Health Check", icon: Activity },
  { path: "/log-meal", label: "Log Meal", icon: UtensilsCrossed },
  { path: "/history", label: "Meal History", icon: ClipboardList },
  { path: "/profile", label: "Profile", icon: User },
];

interface SideNavProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function SideNav({ collapsed = false, onToggleCollapse }: SideNavProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const handleLogoutConfirm = async () => {
    setIsLoggingOut(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    logout();
    navigate("/login");
  };

  const handleLogoutCancel = () => {
    setShowLogoutModal(false);
  };

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
              DiaTracker
            </h1>
            <p
              className="text-[11px] text-[#637c84]"
              style={{ fontFamily: "'Nunito Sans', sans-serif" }}
            >
              Health and Diabetes Tracker
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

      <div className="absolute bottom-20 left-0 right-0 px-4">
        <button
          onClick={handleLogoutClick}
          disabled={isLoggingOut}
          className="w-full flex items-center gap-4 px-4 py-3 rounded-xl cursor-pointer bg-transparent border-[0.8px] border-[rgba(239,68,68,0.2)] hover:bg-[rgba(239,68,68,0.05)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          title={collapsed ? "Logout" : undefined}
        >
          {isLoggingOut ? (
            <Loader2
              size={24}
              className="text-[#ef4444] animate-spin"
            />
          ) : (
            <LogOut
              size={24}
              className="text-[#ef4444]"
              strokeWidth={1.5}
            />
          )}
          {!collapsed && (
            <span
              className="text-[15px] text-[#ef4444] font-medium"
              style={{ fontFamily: "'Geist', sans-serif" }}
            >
              {isLoggingOut ? "Logging out..." : "Logout"}
            </span>
          )}
        </button>
      </div>

      {showLogoutModal && (
        <div
          className="fixed inset-0 bg-black/30 z-[100] flex items-center justify-center px-4"
          onClick={handleLogoutCancel}
        >
          <div
            className="bg-white rounded-3xl w-full max-w-[340px] p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-[rgba(239,68,68,0.1)] rounded-full flex items-center justify-center mx-auto mb-4">
                <LogOut size={24} className="text-[#ef4444]" />
              </div>
              <p
                className="text-[18px] text-[#0d2b35] mb-2"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                Are you sure to logout?
              </p>
              <p
                className="text-[14px] text-[#637c84]"
                style={{
                  fontFamily: "'Nunito Sans', sans-serif",
                }}
              >
                You will need to login again to access your account.
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleLogoutCancel}
                disabled={isLoggingOut}
                className="flex-1 h-[48px] bg-[rgba(226,234,235,0.5)] text-[#0d2b35] rounded-2xl border-none cursor-pointer text-[16px] disabled:opacity-50"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleLogoutConfirm}
                disabled={isLoggingOut}
                className="flex-1 h-[48px] bg-[#ef4444] text-white rounded-2xl border-none cursor-pointer text-[16px] flex items-center justify-center gap-2 disabled:opacity-50"
                style={{
                  fontFamily: "'Geist', sans-serif",
                  fontWeight: 600,
                }}
              >
                {isLoggingOut ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    Logging out...
                  </>
                ) : (
                  "Logout"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

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
