"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useEffect, useState, type ReactNode } from "react";
import { useAuthStore, useLanguageStore, useThemeStore } from "@/store";

function StoreHydration() {
  useEffect(() => {
    useAuthStore.persist.rehydrate();
    useThemeStore.persist.rehydrate();
    useLanguageStore.persist.rehydrate();
  }, []);
  return null;
}

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 2,
            refetchOnWindowFocus: false,
            gcTime: 300_000,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
        <StoreHydration />
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
