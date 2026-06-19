"use client";

import { create } from "zustand";
import type { AppNotification } from "@/types/governance";

interface NotificationState {
  items: AppNotification[];
  push: (item: AppNotification) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  remove: (id: string) => void;
}

export const useNotificationsStore = create<NotificationState>((set) => ({
  items: [],
  push: (item) => set((state) => ({ items: [item, ...state.items].slice(0, 60) })),
  markRead: (id) =>
    set((state) => ({
      items: state.items.map((item) => (item.id === id ? { ...item, read: true } : item)),
    })),
  markAllRead: () =>
    set((state) => ({
      items: state.items.map((item) => ({ ...item, read: true })),
    })),
  remove: (id) => set((state) => ({ items: state.items.filter((item) => item.id !== id) })),
}));

