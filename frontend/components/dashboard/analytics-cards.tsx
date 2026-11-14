"use client";

import React from "react";
import { useEffect, useRef, useState } from "react";
import { Car, CircleParking, LayoutGrid, Percent } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { usePolling } from "@/hooks/use-polling";

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  suffix?: string;
  decimals?: number;
  color: string;
  delay: number;
}

function AnimatedNumber({
  target,
  suffix = "",
  decimals = 0,
}: {
  target: number;
  suffix?: string;
  decimals?: number;
}) {
  const [display, setDisplay] = useState(0);
  const current = useRef(0); // the value on screen right now

  // Glide from whatever is currently shown to the new value. (The old version
  // restarted from 0 on every update, so the numbers kept counting up from 0.)
  useEffect(() => {
    const from = current.current;
    const startedAt = performance.now();
    const duration = 600;
    let raf = 0;

    const step = () => {
      // Use performance.now() (same clock as startedAt) and clamp to 0..1
      const t = Math.min(1, Math.max(0, (performance.now() - startedAt) / duration));
      current.current = from + (target - from) * t;
      setDisplay(current.current);
      if (t < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target]);

  return (
    <span className="animate-count-up font-mono text-3xl font-bold tracking-tight">
      {display.toFixed(decimals)}
      {suffix}
    </span>
  );
}

function StatCard({ icon, label, value, suffix, decimals, color, delay }: StatCardProps) {
  return (
    <Card
      className="group relative overflow-hidden border-border bg-card transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
      style={{ animationDelay: `${delay}ms` }}
    >
      <CardContent className="flex items-center gap-4 p-5">
        <div
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl"
          style={{ backgroundColor: `${color}15` }}
        >
          <div style={{ color }}>{icon}</div>
        </div>

        <div className="flex flex-col gap-0.5">
          <AnimatedNumber target={value} suffix={suffix} decimals={decimals} />
          <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
            {label}
          </span>
        </div>
      </CardContent>

      <div
        className="absolute bottom-0 left-0 h-0.5 w-full opacity-60 transition-opacity group-hover:opacity-100"
        style={{ backgroundColor: color }}
      />
    </Card>
  );
}

// Shape of GET /api/stats. `total` and `occupancy` are older names the backend
// still sends for backwards compatibility.
interface ParkingStats {
  total_slots?: number;
  total?: number;
  occupied?: number;
  available?: number;
  occupancy_rate?: number;
  occupancy?: number;
}

export function AnalyticsCards() {
  const { data: statsData, isOffline } = usePolling<ParkingStats>("/api/stats", 1000);

  const stats = [
    {
      icon: <LayoutGrid className="h-5 w-5" />,
      label: "Total Slots",
      value: statsData?.total_slots ?? statsData?.total ?? 0,
      color: "hsl(199, 89%, 48%)",
      delay: 0,
    },
    {
      icon: <Car className="h-5 w-5" />,
      label: "Occupied",
      value: statsData?.occupied ?? 0,
      color: "hsl(0, 72%, 51%)",
      delay: 100,
    },
    {
      icon: <CircleParking className="h-5 w-5" />,
      label: "Available",
      value: statsData?.available ?? 0,
      color: "hsl(152, 70%, 50%)",
      delay: 200,
    },
    {
      icon: <Percent className="h-5 w-5" />,
      label: "Occupancy",
      value: statsData?.occupancy_rate ?? statsData?.occupancy ?? 0,
      suffix: "%",
      decimals: 1,
      color: "hsl(38, 92%, 50%)",
      delay: 300,
    },
  ];

  return (
    <div className="flex flex-col gap-3">
      {isOffline && (
        <p
          role="status"
          className="rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-500"
        >
          Can&apos;t reach the parking backend. If it runs on free hosting it can take about a
          minute to wake up. Retrying automatically…
        </p>
      )}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>
    </div>
  );
}
