// 회의실 예약 화면. 서버 API는 /api/... 이고 공개 문서는 없어요.
// 아래 RULES는 화면이 지키는 규칙이에요.

const RULES = {
  openTime: "09:00",       // 예약 가능한 첫 시간
  closeTime: "19:00",      // 예약 가능한 마지막 시간
  stepMinutes: 30,         // 30분 단위
  maxMinutes: 120,         // 한 번에 2시간까지
  maxPerDay: 2,            // 한 사람이 하루 2건까지
  titleMax: 30,            // 제목 30자까지
  noWeekend: true,         // 토요일과 일요일은 예약하지 않아요
  noPast: true,            // 지난 시간은 예약하지 않아요
  pageSize: 20,            // 예약 목록은 한 쪽에 20건씩
  peopleMinChars: 2,       // 직원 찾기는 두 글자부터
  peopleMaxResults: 10,    // 직원 찾기 결과는 10명까지 보여 줘요
  maskPhone: true,         // 전화번호 가운데 네 자리는 가려요
  cancelOnlyMine: true,    // 취소 버튼은 내 예약에만 보여 줘요
};

const state = { me: null, page: 1, pages: 1, rooms: [] };
const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: options.body ? { "Content-Type": "application/json" } : {},
    ...options,
  });
  if (response.status === 401) {
    location.href = "/login";
    throw new Error("로그인이 필요해요.");
  }
  const data = await response.json();
  if (!response.ok) {
    const wait = response.headers.get("Retry-After");
    throw new Error(data.error + (wait ? ` (${wait}초 뒤에 다시)` : ""));
  }
  return data;
}

function show(text, ok = false) {
  const box = $("message");
  box.textContent = text;
  box.className = ok ? "message ok" : "message";
  box.hidden = !text;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

const toMinutes = (hhmm) => Number(hhmm.slice(0, 2)) * 60 + Number(hhmm.slice(3, 5));
const toHHMM = (m) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
const todayText = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

function maskPhone(phone) {
  if (!RULES.maskPhone) return phone;
  return phone.replace(/^(\d{3})-(\d{3,4})-(\d{4})$/, "$1-****-$3");
}

// ---------- 회의실 현황 ----------
async function loadRooms() {
  const data = await api("/api/rooms");
  state.rooms = data.rooms;
  $("rooms").innerHTML = data.rooms.map((room) => `
    <article class="room ${room.in_use ? "busy" : ""}">
      <h3>${escapeHtml(room.name)} <small>${room.floor}층 · ${room.seats}명</small></h3>
      <p>${room.in_use ? `지금 사용 중: ${escapeHtml(room.in_use.title)} (~${room.in_use.end})` : "지금 비어 있어요"}</p>
      <p class="hint">${room.next ? `다음 예약 ${room.next.start} ${escapeHtml(room.next.title)}` : "오늘 남은 예약이 없어요"} · 오늘 ${room.bookings}건</p>
    </article>`).join("");
  $("book-room").innerHTML = data.rooms.map((r) => `<option value="${r.id}">${escapeHtml(r.name)} (${r.floor}층, ${r.seats}명)</option>`).join("");
}

// ---------- 예약 목록 ----------
async function loadList() {
  const params = new URLSearchParams({ page: state.page, size: RULES.pageSize });
  if ($("list-date").value) params.set("date", $("list-date").value);
  if ($("list-mine").checked) params.set("mine", "1");
  const data = await api(`/api/reservations?${params}`);
  state.pages = data.pages;
  $("list-body").innerHTML = data.items.map((r) => {
    const mine = r.owner_id === state.me.id;
    const button = !RULES.cancelOnlyMine || mine ? `<button class="cancel" data-id="${r.id}">취소</button>` : "";
    return `<tr class="${mine ? "mine" : ""}"><td>${r.id}</td><td>${r.date}</td><td>${r.start}~${r.end}</td>
      <td>${escapeHtml(r.room_name)}</td><td>${escapeHtml(r.title)}</td><td>${escapeHtml(r.owner_name)}</td><td>${button}</td></tr>`;
  }).join("") || `<tr><td colspan="7">예약이 없어요.</td></tr>`;
  $("page-info").textContent = `${data.page} / ${data.pages}쪽 (모두 ${data.total}건)`;
  $("prev").disabled = data.page <= 1;
  $("next").disabled = data.page >= data.pages;
}

async function cancelReservation(id) {
  if (!confirm(`${id}번 예약을 취소할까요?`)) return;
  await api(`/api/reservations/${id}`, { method: "DELETE" });
  show(`${id}번 예약을 취소했어요.`, true);
  await loadList();
}

// ---------- 예약 만들기 ----------
function fillTimes() {
  const options = [];
  for (let m = toMinutes(RULES.openTime); m <= toMinutes(RULES.closeTime); m += RULES.stepMinutes) {
    options.push(`<option>${toHHMM(m)}</option>`);
  }
  $("book-start").innerHTML = options.slice(0, -1).join("");
  $("book-end").innerHTML = options.slice(1).join("");
  $("book-date").min = todayText();
  $("book-date").value = todayText();
  $("book-title").maxLength = RULES.titleMax;
}

async function checkBooking(form) {
  const start = toMinutes(form.start), end = toMinutes(form.end);
  if (end <= start) return "끝나는 시간이 시작 시간보다 뒤여야 해요.";
  if (end - start > RULES.maxMinutes) return `한 번에 ${RULES.maxMinutes / 60}시간까지 예약할 수 있어요.`;
  const day = new Date(`${form.date}T00:00:00`).getDay();
  if (RULES.noWeekend && (day === 0 || day === 6)) return "주말에는 예약할 수 없어요.";
  if (RULES.noPast && new Date(`${form.date}T${form.start}:00`) < new Date()) return "지난 시간은 예약할 수 없어요.";
  if (form.title.trim().length > RULES.titleMax) return `제목은 ${RULES.titleMax}자까지 적어 주세요.`;
  const mine = await api(`/api/reservations?${new URLSearchParams({ date: form.date, mine: "1", size: RULES.pageSize })}`);
  if (mine.total >= RULES.maxPerDay) return `한 사람이 하루 ${RULES.maxPerDay}건까지 예약할 수 있어요.`;
  return "";
}

async function submitBooking(event) {
  event.preventDefault();
  const form = {
    room_id: $("book-room").value, date: $("book-date").value,
    start: $("book-start").value, end: $("book-end").value, title: $("book-title").value,
  };
  const problem = await checkBooking(form);
  if (problem) return show(problem);
  const data = await api("/api/reservations", { method: "POST", body: JSON.stringify(form) });
  show(`${data.reservation.id}번으로 예약했어요. ${data.reservation.room_name} ${form.date} ${form.start}~${form.end}`, true);
  $("book-title").value = "";
}

// ---------- 직원 찾기 ----------
let peopleTimer = null;
async function searchPeople() {
  const q = $("people-q").value.trim();
  if (q.length < RULES.peopleMinChars) {
    $("people-body").innerHTML = "";
    $("people-info").textContent = `${RULES.peopleMinChars}글자 이상 적어 주세요.`;
    return;
  }
  const data = await api(`/api/people?${new URLSearchParams({ q })}`);
  const shown = data.items.slice(0, RULES.peopleMaxResults);
  $("people-body").innerHTML = shown.map((p) => `<tr><td>${escapeHtml(p.name)}</td><td>${escapeHtml(p.team)}</td>
    <td>${maskPhone(p.phone)}</td><td>${escapeHtml(p.email)}</td></tr>`).join("");
  $("people-info").textContent = data.items.length > shown.length
    ? `${RULES.peopleMaxResults}명까지 보여 줘요. 더 자세히 적어 주세요.` : `${shown.length}명을 찾았어요.`;
}

// ---------- 시작 ----------
function openTab(name) {
  document.querySelectorAll("nav button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tab").forEach((t) => { t.hidden = t.id !== `tab-${name}`; });
  show("");
  const loaders = { rooms: loadRooms, list: loadList };
  if (loaders[name]) loaders[name]().catch((e) => show(e.message));
}

async function start() {
  state.me = await api("/api/me");
  $("me").textContent = `${state.me.name} (${state.me.team})`;
  fillTimes();
  document.querySelectorAll("nav button").forEach((b) => b.addEventListener("click", () => openTab(b.dataset.tab)));
  $("prev").addEventListener("click", () => { state.page -= 1; loadList().catch((e) => show(e.message)); });
  $("next").addEventListener("click", () => { state.page += 1; loadList().catch((e) => show(e.message)); });
  $("list-date").addEventListener("change", () => { state.page = 1; loadList().catch((e) => show(e.message)); });
  $("list-mine").addEventListener("change", () => { state.page = 1; loadList().catch((e) => show(e.message)); });
  $("list-body").addEventListener("click", (event) => {
    const id = event.target.dataset && event.target.dataset.id;
    if (id) cancelReservation(id).catch((e) => show(e.message));
  });
  $("book-form").addEventListener("submit", (event) => submitBooking(event).catch((e) => show(e.message)));
  $("people-q").addEventListener("input", () => {
    clearTimeout(peopleTimer);
    peopleTimer = setTimeout(() => searchPeople().catch((e) => show(e.message)), 300);
  });
  await loadRooms();
}

start().catch((e) => show(e.message));
