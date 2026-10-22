// 목록 맨 뒤에 새 글을 붙인 새 배열을 돌려줘요.
export function addEntry(entries, name, message) {
  return [...entries, { name, message }]
}
