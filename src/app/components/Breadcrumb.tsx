import { ChevronRight } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  onClick?: () => void;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export default function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-2 mb-4" aria-label="Breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <div key={index} className="flex items-center gap-2">
            {item.onClick && !isLast ? (
              <button
                onClick={item.onClick}
                className="text-[14px] text-[#1e6177] hover:underline bg-transparent border-none cursor-pointer"
                style={{ fontFamily: "'Nunito Sans', sans-serif", fontWeight: 600 }}
              >
                {item.label}
              </button>
            ) : (
              <span
                className={`text-[14px] ${
                  isLast ? "text-[#0d2b35] font-semibold" : "text-[#637c84]"
                }`}
                style={{ fontFamily: "'Nunito Sans', sans-serif" }}
              >
                {item.label}
              </span>
            )}
            {!isLast && <ChevronRight size={16} className="text-[#637c84]" />}
          </div>
        );
      })}
    </nav>
  );
}
