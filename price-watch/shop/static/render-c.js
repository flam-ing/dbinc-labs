// C 구조(15~22일): HTML 안의 <script id="__SHOP_STATE__">에 든 JSON으로 화면을 그려요.
// 서버가 보낸 원래 HTML에는 상품 카드가 없고 JSON만 있어요.
(function () {
  const state = JSON.parse(document.getElementById('__SHOP_STATE__').textContent);
  const won = n => n.toLocaleString('ko-KR') + '원';
  const list = document.getElementById('list');
  list.classList.remove('loading');
  list.innerHTML = state.products.map(p => {
    const price = p.pricing.current < p.pricing.regular
      ? `<del>${won(p.pricing.regular)}</del> <strong>${won(p.pricing.current)}</strong>`
      : `<strong>${won(p.pricing.current)}</strong>`;
    return `<div class="card"><p class="card__cat">${p.group}</p><h3>${p.label}</h3><div>${price}</div></div>`;
  }).join('');
})();
