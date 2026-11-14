"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePolling } from "@/hooks/use-polling";
import { LayoutGrid } from "lucide-react";

// One entry of GET /api/slots
interface LiveSlot {
  id: string; // "P1", "P2", ...
  occupied: boolean;
}

function SlotCell({ slot }: { slot: LiveSlot }) {
  const [isHovered, setIsHovered] = useState(false);

  const isOccupied = slot.occupied;

  return (
    <button
      type="button"
      className={`relative flex h-10 items-center justify-center rounded-md border font-mono text-[10px] font-bold transition-all duration-200 ${
        isOccupied
          ? "border-destructive/30 bg-destructive/15 text-destructive hover:border-destructive/60 hover:bg-destructive/25"
          : "border-primary/30 bg-primary/10 text-primary hover:border-primary/60 hover:bg-primary/25"
      } ${isHovered ? "scale-110 shadow-lg z-10" : ""}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label={`Slot ${slot.id}: ${isOccupied ? "occupied" : "available"}`}
    >
      {slot.id}
      {isHovered && (
        <div className="absolute -top-8 left-1/2 z-20 -translate-x-1/2 whitespace-nowrap rounded-md bg-popover px-2 py-1 text-[10px] text-popover-foreground shadow-lg">
          {isOccupied ? "Occupied" : "Available"}
        </div>
      )}
    </button>
  );
}

export function ParkingGrid() {
  // Live slot states from the Flask backend (same data the CCTV overlay uses)
  const { data: slots, isOffline } = usePolling<LiveSlot[]>("/api/slots", 1000);

  return (
    <Card className="border-border bg-card">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <LayoutGrid className="h-4 w-4 text-accent" />
          <CardTitle className="text-sm font-semibold text-foreground">
            Parking Map - Real-time Grid
          </CardTitle>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-sm bg-primary/60" />
            <span className="text-[10px] text-muted-foreground">Available</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-sm bg-destructive/60" />
            <span className="text-[10px] text-muted-foreground">Occupied</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <div className="rounded-lg border border-border bg-background/50 p-4">
          {slots && slots.length > 0 ? (
            <div className="grid grid-cols-5 gap-1.5 sm:grid-cols-7">
              {slots.map((slot) => (
                <SlotCell key={slot.id} slot={slot} />
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-xs text-muted-foreground">
              {isOffline
                ? "Backend not reachable yet - retrying automatically…"
                : "Waiting for live slot data…"}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
