import type { Grade } from "./grades";

// 화면에서 보여 줄 적립 포인트 (config.py의 RATE_SCHEDULE과 같은 규칙으로 맞춰 둘 것. 새것이 먼저)
const RATE_SCHEDULE: [string, Partial<Record<Grade, number>>][] = [
  ["2027-01-01", { 일반: 0.02, VIP: 0.03, 골드: 0.05 }],
  ["2026-11-01", { 일반: 0.02, VIP: 0.03 }],
  ["0000-00-00", { 일반: 0.01, VIP: 0.03 }],
];

export function calcPoint(amount: number, grade: Grade, date: string = todayString()): number {
  const rates = RATE_SCHEDULE.find(([startDate]) => date >= startDate)![1];
  return Math.floor(amount * rates[grade]!);
}

function todayString(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}
