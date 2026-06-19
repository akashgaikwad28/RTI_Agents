"use client";

import { useUIStore } from "@/stores/ui-store";
import { messages } from "@/i18n/messages";

export function useTranslations() {
  const locale = useUIStore((state) => state.locale);
  return (key: keyof (typeof messages)["en"]) => messages[locale][key] ?? messages.en[key];
}

