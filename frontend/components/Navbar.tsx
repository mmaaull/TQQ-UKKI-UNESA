"use client";

import { BookOpen, GraduationCap, Menu, X } from "lucide-react";
import { useState } from "react";

export type NavbarProps = {
  activeItem?: string;
  items?: string[];
  onOpenGuide?: () => void;
  onNavigate?: (item: string) => void;
};

const defaultItems = ["Dashboard", "Upload", "Hasil Rekap", "Validasi", "Export", "Rapikan"];

export function Navbar({
  activeItem = "Dashboard",
  items = defaultItems,
  onOpenGuide,
  onNavigate,
}: NavbarProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  function handleItemClick(item: string) {
    if (onNavigate) {
      onNavigate(item);
    }
    setIsMobileMenuOpen(false);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-5 px-5 sm:px-8 lg:px-10">
        {/* Brand Logo & Title */}
        <div
          onClick={() => handleItemClick("Dashboard")}
          className="flex shrink-0 items-center gap-3 cursor-pointer"
        >
          <div className="grid size-10 place-items-center rounded-xl bg-blue-600 text-white shadow-sm shadow-blue-600/25">
            <GraduationCap size={22} strokeWidth={2.3} />
          </div>
          <div className="leading-tight">
            <p className="text-[17px] font-bold tracking-tight text-blue-700">UKKI UNESA</p>
            <p className="mt-0.5 text-[11px] font-medium text-slate-500">TQQ Akbar</p>
          </div>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden h-full items-center gap-6 lg:flex" aria-label="Navigasi utama">
          {items.map((item) => (
            <button
              onClick={() => handleItemClick(item)}
              className={
                item === activeItem
                  ? "h-full border-b-2 border-blue-700 text-sm font-bold text-blue-700 transition"
                  : "h-full text-sm font-medium text-slate-500 transition hover:text-blue-700"
              }
              key={item}
              type="button"
            >
              {item}
            </button>
          ))}
        </nav>

        {/* Header Right Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button
            onClick={onOpenGuide}
            className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3.5 py-2 text-xs font-semibold text-blue-700 transition hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            type="button"
          >
            <BookOpen size={16} />
            <span>Panduan</span>
          </button>

          {/* Mobile Hamburger Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="grid size-10 place-items-center rounded-lg text-slate-600 hover:bg-slate-100 lg:hidden"
            type="button"
            aria-label="Buka navigasi"
          >
            {isMobileMenuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer Overlay */}
      {isMobileMenuOpen && (
        <div className="border-b border-slate-200 bg-white px-5 py-4 shadow-lg lg:hidden">
          <nav className="flex flex-col gap-2" aria-label="Navigasi mobile">
            {items.map((item) => (
              <button
                key={item}
                onClick={() => handleItemClick(item)}
                className={`rounded-xl px-4 py-2.5 text-left text-sm font-semibold transition ${
                  item === activeItem
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
                type="button"
              >
                {item}
              </button>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
