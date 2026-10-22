import React, { useState } from "react";
import { calcPoint } from "./points";
import GradeBadge from "./GradeBadge";

const ADMIN_PASSWORD = "cafe1234"; // cafe.py랑 똑같이 맞춰 둘 것

type Member = { id: string; name: string; total: number; points: number; grade: any };

export default function App({ members }: { members: Member[] }) {
  const [keyword, setKeyword] = useState("");

  // 회원 한 명 카드 (누르면 펼쳐져요)
  function HoewonCard({ m }: { m: Member }) {
    const [open, setOpen] = useState(false);
    return (
      <li onClick={() => setOpen(!open)}>
        {m.name} <GradeBadge grade={m.grade} />
        {open && <p>5,000원 주문하면 {calcPoint(5000, m.grade)}점 적립</p>}
      </li>
    );
  }

  const list = members.filter((m) => m.name.includes(keyword));
  return (
    <div>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="이름 찾기" />
      {keyword === ADMIN_PASSWORD && <button onClick={() => alert("관리자 모드")}>관리자</button>}
      <ul>
        {list.map((m) => (
          <HoewonCard key={m.id} m={m} />
        ))}
      </ul>
    </div>
  );
}
