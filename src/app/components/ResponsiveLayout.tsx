import { ReactNode, useState, useEffect } from "react";
import BottomNav from "./BottomNav";
import SideNav from "./SideNav";

interface ResponsiveLayoutProps {
  children: ReactNode;
  showBottomNav?: boolean;
}

type ViewportSize = "mobile" | "tablet" | "desktop";

export default function ResponsiveLayout({ children, showBottomNav = true }: ResponsiveLayoutProps) {
  const [viewportSize, setViewportSize] = useState<ViewportSize>("mobile");
  const [sideNavCollapsed, setSideNavCollapsed] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= 1024) {
        setViewportSize("desktop");
        setSideNavCollapsed(false); // Always expanded on desktop
      } else if (width >= 768) {
        setViewportSize("tablet");
        // Keep current collapsed state on tablet
      } else {
        setViewportSize("mobile");
      }
    };

    // Initial check
    handleResize();

    // Add event listener
    window.addEventListener("resize", handleResize);

    // Cleanup
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const isMobile = viewportSize === "mobile";
  const isTablet = viewportSize === "tablet";
  const isDesktop = viewportSize === "desktop";

  // Calculate content padding based on navigation type and state
  const getContentPadding = () => {
    if (isMobile) {
      return showBottomNav ? "pb-[80px]" : "";
    }
    // Tablet or Desktop - has side nav
    if (sideNavCollapsed) {
      return "pl-[80px]";
    }
    return "pl-[240px]";
  };

  return (
    <div className="min-h-screen bg-[#f4f8f8]">
      {/* Side Navigation for Tablet and Desktop */}
      {(isTablet || isDesktop) && (
        <SideNav
          collapsed={sideNavCollapsed}
          onToggleCollapse={isTablet ? () => setSideNavCollapsed(!sideNavCollapsed) : undefined}
        />
      )}

      {/* Main Content */}
      <div className={`min-h-screen transition-all duration-300 ${getContentPadding()}`}>
        {children}
      </div>

      {/* Bottom Navigation for Mobile */}
      {isMobile && showBottomNav && <BottomNav />}
    </div>
  );
}
