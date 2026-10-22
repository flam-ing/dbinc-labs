import type { Grade } from "./grades";

// 화면에서 보여 줄 적립 포인트 (config.py의 POINT_RATES와 같은 규칙으로 맞춰 둘 것)
const POINT_RATES: Record<Grade, number> = { 일반: 0.01, VIP: 0.03 };

export function calcPoint(amount: number, grade: Grade): number {
  return Math.floor(amount * POINT_RATES[grade]);
}
