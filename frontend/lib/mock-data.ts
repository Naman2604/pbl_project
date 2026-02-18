export const parkingStats = {
  totalSlots: 240,
  occupiedSlots: 167,
  availableSlots: 73,
  occupancyPercentage: 69.6,
};

export type SlotStatus = "occupied" | "available";

export interface ParkingSlot {
  id: string;
  status: SlotStatus;
  row: string;
  number: number;
}

export const parkingSlots: ParkingSlot[] = (() => {
  const rows = ["A", "B", "C", "D", "E", "F"];
  const slotsPerRow = 10;
  const slots: ParkingSlot[] = [];

  for (const row of rows) {
    for (let num = 1; num <= slotsPerRow; num++) {
      slots.push({
        id: `${row}${num}`,
        status: Math.random() > 0.3 ? "occupied" : "available",
        row,
        number: num,
      });
    }
  }
  return slots;
})();

export const hourlyUsage = [
  { hour: "6AM", occupied: 45, available: 195 },
  { hour: "7AM", occupied: 89, available: 151 },
  { hour: "8AM", occupied: 156, available: 84 },
  { hour: "9AM", occupied: 198, available: 42 },
  { hour: "10AM", occupied: 210, available: 30 },
  { hour: "11AM", occupied: 205, available: 35 },
  { hour: "12PM", occupied: 220, available: 20 },
  { hour: "1PM", occupied: 215, available: 25 },
  { hour: "2PM", occupied: 195, available: 45 },
  { hour: "3PM", occupied: 180, available: 60 },
  { hour: "4PM", occupied: 190, available: 50 },
  { hour: "5PM", occupied: 225, available: 15 },
  { hour: "6PM", occupied: 200, available: 40 },
  { hour: "7PM", occupied: 167, available: 73 },
];

export const slotUtilization = [
  { zone: "Zone A", utilization: 85 },
  { zone: "Zone B", utilization: 72 },
  { zone: "Zone C", utilization: 91 },
  { zone: "Zone D", utilization: 58 },
  { zone: "Zone E", utilization: 67 },
  { zone: "Zone F", utilization: 44 },
];

export const aiInsights = {
  peakTime: "12:00 PM - 1:00 PM",
  averageOccupancy: "76.4%",
  demandTrend: "Increasing",
  alerts: [
    { type: "warning" as const, message: "Zone C approaching full capacity (91%)" },
    { type: "info" as const, message: "Predicted peak demand at 5:30 PM today" },
    { type: "warning" as const, message: "Camera 3 intermittent connection" },
  ],
};
