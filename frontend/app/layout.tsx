import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import React from "react";
import "./globals.css";

import { Navbar } from "@/components/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Rekap Nilai TQQ Akbar UNESA",
  description: "Frontend Rekap Nilai TQQ Akbar UNESA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="id"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#f8fafc] text-slate-900">
        <Navbar />
        <div className="flex-1">{children}</div>
        <footer className="border-t border-slate-200 bg-white py-6 text-xs text-slate-500">
          <div className="mx-auto flex max-w-[1440px] flex-col justify-between gap-3 px-4 sm:flex-row sm:px-8 lg:px-10">
            <p>© 2026 UKKI UNESA — Sistem Manajemen Akademik</p>
            <button className="transition hover:text-blue-700" type="button">
              Kebijakan Privasi
            </button>
          </div>
        </footer>
      </body>
    </html>
  );
}
