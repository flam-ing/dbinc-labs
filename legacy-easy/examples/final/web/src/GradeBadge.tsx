import type { Grade } from "./grades";

export default function GradeBadge({ grade }: { grade: Grade }) {
  const color = grade === "골드" ? "gold" : grade === "VIP" ? "orange" : "gray";
  return <span style={{ color }}>{grade}</span>;
}
