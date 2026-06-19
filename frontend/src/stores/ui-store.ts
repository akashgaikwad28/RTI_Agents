"use client";

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

const storage = {
  getItem: (name: string) => (typeof window === "undefined" ? null : window.localStorage.getItem(name)),
  setItem: (name: string, value: string) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(name, value);
    }
  },
  removeItem: (name: string) => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(name);
    }
  },
};

interface UIState {
  locale: "en" | "hi" | "mr";
  language: "en" | "hi" | "mr";
  sidebarOpen: boolean;
  highContrast: boolean;
  theme: "light" | "dark";
  setLocale: (locale: "en" | "hi" | "mr") => void;
  setLanguage: (locale: "en" | "hi" | "mr") => void;
  setSidebarOpen: (value: boolean) => void;
  toggleContrast: () => void;
  setTheme: (theme: "light" | "dark") => void;
  toggleTheme: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      locale: "en",
      language: "en",
      sidebarOpen: false,
      highContrast: false,
      theme: "dark",
      setLocale: (locale) => set({ locale, language: locale }),
      setLanguage: (language) => set({ language, locale: language }),
      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      toggleContrast: () => set((state) => ({ highContrast: !state.highContrast })),
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === "dark" ? "light" : "dark" })),
    }),
    { name: "rti-ui", storage: createJSONStorage(() => storage) }
  )
);

export const useThemeStore = useUIStore;
