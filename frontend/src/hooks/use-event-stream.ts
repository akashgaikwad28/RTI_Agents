"use client";

import { useEffect } from "react";
import { config } from "@/config";

interface StreamHandlers {
  onMessage?: (payload: unknown) => void;
  onError?: (error: Event) => void;
}

export function useEventStream(path: string | null, handlers: StreamHandlers) {
  useEffect(() => {
    if (!path) {
      return;
    }
    const source = new EventSource(`${config.api.baseUrl}${path}`);
    source.onmessage = (event) => {
      try {
        handlers.onMessage?.(JSON.parse(event.data));
      } catch {
        handlers.onMessage?.(event.data);
      }
    };
    source.onerror = (error) => {
      handlers.onError?.(error);
      source.close();
    };
    return () => source.close();
  }, [handlers, path]);
}

