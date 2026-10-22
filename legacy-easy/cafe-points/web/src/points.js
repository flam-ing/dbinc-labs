// 화면에서 보여 줄 적립 포인트 (cafe.py와 같은 규칙으로 맞춰 둘 것)
export function calcPoint(amount, grade) {
  console.log("calcPoint 들어옴", amount, grade); // 테스트용 (나중에 지울 것)
  if (grade == "VIP") return Math.floor(amount * 0.03);
  return Math.floor(amount * 0.01);
}
