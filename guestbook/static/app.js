const form = document.querySelector('#entry-form');
const button = document.querySelector('#submit-button');
const list = document.querySelector('#entry-list');
const formStatus = document.querySelector('#form-status');
const listStatus = document.querySelector('#list-status');

function status(element, text, error = false) {
  element.textContent = text;
  element.classList.toggle('error', error);
}

async function loadEntries() {
  status(listStatus, '기록을 불러오는 중…');
  try {
    const response = await fetch('/api/entries');
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '목록을 불러오지 못했습니다.');
    list.replaceChildren();
    for (const entry of data.entries) {
      const item = document.createElement('li');
      const meta = document.createElement('div');
      meta.className = 'entry-meta';
      const name = document.createElement('span');
      name.className = 'entry-name';
      name.textContent = entry.name;
      const time = document.createElement('time');
      time.dateTime = entry.created_at;
      time.textContent = new Date(entry.created_at).toLocaleString('ko-KR');
      const message = document.createElement('p');
      message.className = 'entry-message';
      message.textContent = entry.message;
      meta.append(name, time);
      item.append(meta, message);
      list.append(item);
    }
    status(listStatus, data.entries.length ? `${data.entries.length}개의 기록` : '아직 기록이 없습니다. 첫 문장을 남겨주세요.');
  } catch (error) {
    status(listStatus, '목록을 불러오지 못했습니다. 서버 실행 상태를 확인하고 새로고침해 주세요.', true);
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  button.disabled = true;
  status(formStatus, '저장하는 중…');
  try {
    const response = await fetch('/api/entries', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: form.elements.name.value, message: form.elements.message.value}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '저장하지 못했습니다.');
    form.elements.message.value = '';
    status(formStatus, `저장했습니다. 기록 번호 #${data.entry.id}`);
    await loadEntries();
  } catch (error) {
    status(formStatus, error.message || '서버 연결을 확인해 주세요.', true);
  } finally {
    button.disabled = false;
  }
});

document.querySelector('#refresh-button').addEventListener('click', loadEntries);
loadEntries();
