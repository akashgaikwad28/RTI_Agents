"use client";

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { AppUser, AuthTokens, UserRole } from "@/types/governance";

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

function syncCookies(user: AppUser | null, tokens: AuthTokens | null) {
  if (typeof document === "undefined") {
    return;
  }
  if (!user || !tokens?.accessToken) {
    document.cookie = "rti_session=; Max-Age=0; path=/";
    document.cookie = "rti_role=; Max-Age=0; path=/";
    return;
  }
  document.cookie = `rti_session=${tokens.accessToken}; path=/; SameSite=Lax`;
  document.cookie = `rti_role=${user.role}; path=/; SameSite=Lax`;
}

interface AuthStoreState {
  user: AppUser | null;
  tokens: AuthTokens | null;
  hydrated: boolean;
  setHydrated: (value: boolean) => void;
  login: (user: AppUser, tokens: AuthTokens) => void;
  logout: () => void;
  updateProfile: (patch: Partial<AppUser>) => void;
  setRole: (role: UserRole) => void;
}

export const useAuthAppStore = create<AuthStoreState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      hydrated: false,
      setHydrated: (hydrated) => set({ hydrated }),
      login: (user, tokens) => {
        syncCookies(user, tokens);
        set({ user, tokens });
      },
      logout: () => {
        syncCookies(null, null);
        set({ user: null, tokens: null });
      },
      updateProfile: (patch) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...patch } : null,
        })),
      setRole: (role) =>
        set((state) => {
          const nextUser = state.user ? { ...state.user, role } : null;
          syncCookies(nextUser, state.tokens);
          return { user: nextUser };
        }),
    }),
    {
      name: "rti-auth-v2",
      storage: createJSONStorage(() => storage),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
        syncCookies(state?.user ?? null, state?.tokens ?? null);
      },
    }
  )
);

