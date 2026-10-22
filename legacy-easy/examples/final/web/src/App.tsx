import React, { useState } from "react";
import MemberCard from "./MemberCard";
import type { Member } from "./types";

export default function App({ members }: { members: Member[] }) {
  const [keyword, setKeyword] = useState("");

  const list = members.filter((m) => m.name.includes(keyword));
  return (
    <div>
      <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="이름 찾기" />
      <ul>
        {list.map((m) => (
          <MemberCard key={m.id} member={m} />
        ))}
      </ul>
    </div>
  );
}
