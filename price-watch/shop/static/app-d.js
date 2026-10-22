// D 구조(23일부터): 화면이 /api/catalog를 쪽마다 불러서 그려요.
// 429를 받으면 Retry-After만큼 기다렸다가 다시 불러요.
(async function () {
  const app = document.getElementById('app');
  const won = n => n.toLocaleString('ko-KR') + '원';
  const wait = s => new Promise(r => setTimeout(r, s * 1000));
  const items = [];
  let page = 1;
  while (page) {
    const res = await fetch('/api/catalog?page=' + page);
    if (res.status === 429) { await wait(Number(res.headers.get('Retry-After') || 1)); continue; }
    const data = await res.json();
    items.push(...data.items);
    page = data.next;
  }
  app.innerHTML = items.map(p => {
    const price = p.price.amount < p.price.list
      ? `<del>${won(p.price.list)}</del> <strong>${won(p.price.amount)}</strong>`
      : `<strong>${won(p.price.amount)}</strong>`;
    return `<div class="card"><p class="card__cat">${p.category}</p><h3>${p.title}</h3><div>${price}</div></div>`;
  }).join('');
})();
