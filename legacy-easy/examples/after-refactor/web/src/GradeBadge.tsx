import type { Grade } from "./grades";

export default function GradeBadge({ grade }: { grade: Grade }) {
  const color = grade === "VIP" ? "gold" : "gray";
  return <span style={{ color }}>{grade}</span>;
}
