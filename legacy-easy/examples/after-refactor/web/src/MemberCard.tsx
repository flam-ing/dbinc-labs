import React, { useState } from "react";
import { calcPoint } from "./points";
import GradeBadge from "./GradeBadge";
import type { Member } from "./types";

// 회원 한 명 카드 (누르면 펼쳐져요)
export default function MemberCard({ member }: { member: Member }) {
  const [open, setOpen] = useState(false);
  return (
    <li onClick={() => setOpen(!open)}>
      {member.name} <GradeBadge grade={member.grade} />
      {open && <p>5,000원 주문하면 {calcPoint(5000, member.grade)}점 적립</p>}
    </li>
  );
}
