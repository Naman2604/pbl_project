"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

/**
 * Fetches `${API_URL}${path}` repeatedly and returns the latest data.
 *
 * - The next request only starts after the previous one finished, so a slow
 *   server (e.g. free hosting waking up) never gets a pile of overlapping calls.
 * - `isOffline` becomes true after 2 failed requests in a row and goes back to
 *   false by itself as soon as the backend answers again.
 */
export function usePolling<T>(path: string, intervalMs = 1000) {
  const [data, setData] = useState<T | null>(null);
  const [failures, setFailures] = useState(0);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const tick = async () => {
      try {
        const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as T;
        if (!cancelled) {
          setData(json);
          setFailures(0);
        }
      } catch {
        if (!cancelled) setFailures((n) => n + 1);
      } finally {
        if (!cancelled) timer = setTimeout(tick, intervalMs);
      }
    };

    tick();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [path, intervalMs]);

  return { data, isOffline: failures >= 2 };
}
