/* 게임 키트 고르기 부품 (1일차 3교시 발표 s3.html과 deck-kit.html이 써요)
 *
 * - 빌드 없이 <script src="labs/game-kit/picker.js"></script>로 불러오면 window.GameKit이 생겨요.
 * - 장르·주인공·장애물·내 아이디어를 고르면 Claude 채팅에 붙여 넣을 프롬프트가 바로 바뀌어요.
 * - 고른 값은 한 곳(GameKit.getChoice)에 있고, 같은 페이지의 모든 상자가 같이 바뀌어요.
 * - 클래스 이름은 모두 gk-로 시작해요. 부품 CSS는 처음 그릴 때 <style id="gk-style">로 한 번 넣어요.
 * - 발표 무대(1920×1080을 transform으로 줄인 것) 안에서도 쓰려고 position: fixed를 쓰지 않고, 크기는 em으로만 정해요.
 *   상자의 font-size 하나로 크기를 맞춰요. 발표 엔진이 키를 가로채지 않게 입력칸의 키는 여기서 막아요.
 *
 * 쓰는 법은 $SP/boards2/_ref_minigame.md 8절과 s3.html의 .picker, .picker-prompt 장면을 보면 돼요.
 *   GameKit.mount(el, { view: 'full' | 'short', idea: true, random: true, links: [{ text, href }] })
 *   GameKit.mountPrompt(el, { kind: 'game' | 'poster' | 'music' | 'video' | 'merge', variant: 'ask' | 'en' | 'ko', tabs: true })
 *   GameKit.buildPrompt(choice), GameKit.mediaPrompts(choice), GameKit.mergePrompt(choice)
 *   GameKit.getChoice(), GameKit.setChoice({ genre, hero, obstacle, idea }), GameKit.subscribe(fn)
 *   GameKit.copyText(text, elementToSelect)
 */
(function () {
  'use strict';
  if (window.GameKit) return;

  /* ---------- 고르기 자료 ---------- */

  // 프롬프트 안에서 고른 말을 표시하는 표지예요. 화면에서는 주황 칠, 복사할 때는 지워요.
  var HL_OPEN = '\u0001', HL_CLOSE = '\u0002';
  function hl(text) { return HL_OPEN + text + HL_CLOSE; }
  function strip(text) { return String(text).split(HL_OPEN).join('').split(HL_CLOSE).join(''); }

  // 받침을 보고 조사를 골라요. 한글이 아니면 '이(가)'처럼 둘 다 써요.
  function jong(word) {
    var s = String(word || '').trim();
    var c = s.charCodeAt(s.length - 1);
    if (!(c >= 0xac00 && c <= 0xd7a3)) return -1;
    return (c - 0xac00) % 28;
  }
  var JOSA = { '이가': ['이', '가'], '을를': ['을', '를'], '은는': ['은', '는'], '과와': ['과', '와'], '으로': ['으로', '로'] };
  function jo(word, type) {
    var j = jong(word), p = JOSA[type];
    if (j < 0) return p[0] + '(' + p[1] + ')';
    if (type === '으로') return (j === 0 || j === 8) ? '로' : '으로'; // ㄹ 받침은 '로'
    return j ? p[0] : p[1];
  }

  var HEROES = [
    { id: 'rabbit', ko: '토끼', en: 'a cute white rabbit', one: 'rabbit' },
    { id: 'cat', ko: '고양이', en: 'a cute orange cat', one: 'cat' },
    { id: 'puppy', ko: '강아지', en: 'a happy little puppy', one: 'puppy' },
    { id: 'penguin', ko: '펭귄', en: 'a chubby little penguin', one: 'penguin' },
    { id: 'dino', ko: '공룡', en: 'a little green dinosaur', one: 'dinosaur' },
    { id: 'robot', ko: '로봇', en: 'a small round robot', one: 'robot' },
    { id: 'ship', ko: '우주선', en: 'a small cyan spaceship', one: 'spaceship' },
    { id: 'elephant', ko: '코끼리', en: 'a baby elephant', one: 'elephant' }
  ];

  var OBSTACLES = [
    { id: 'carrot', ko: '당근', en: 'orange carrots', one: 'carrot' },
    { id: 'meteor', ko: '운석', en: 'small meteors', one: 'meteor' },
    { id: 'car', ko: '자동차', en: 'toy cars', one: 'car' },
    { id: 'bug', ko: '버그', en: 'little green bugs', one: 'bug' },
    { id: 'mail', ko: '메일', en: 'flying email envelopes', one: 'envelope' },
    { id: 'cactus', ko: '선인장', en: 'cactuses', one: 'cactus' },
    { id: 'snowball', ko: '눈덩이', en: 'snowballs', one: 'snowball' },
    { id: 'cloud', ko: '비구름', en: 'grumpy rain clouds', one: 'rain cloud' }
  ];

  function W(item) { return hl(item.ko); }
  function E(text) { return hl(text); }

  var EASY = '처음 하는 사람도 끝까지 갈 수 있게 쉽게 만들어 줘. 부딪힘 판정은 그림보다 작게 잡아 줘.';
  var MOVE = ['키보드 ←, →', '화면 아래 왼쪽·오른쪽 버튼(누르고 있으면 계속 움직여요)', '게임 화면을 손가락이나 마우스로 끌면 주인공이 따라와요'];
  var LIVES = '5개. 부딪히면 1.5초 동안 깜빡이며 무적이에요. 다 잃으면 게임 오버 화면과 다시 하기 버튼을 보여 줘.';

  var GENRES = [
    {
      id: 'dodge', ko: '피하기',
      rule: function (h, o) { return '위에서 떨어지는 ' + W(o) + jo(o.ko, '을를') + ' 좌우로 움직여 피해요.'; },
      hero: function (h) { return W(h) + '. 화면 맨 아래에서 좌우로 움직여요.'; },
      obstacle: function (o) { return W(o) + '. 위에서 천천히 떨어져요.'; },
      score: '1초에 20점. 300점(약 15초)이 되면 클리어예요.',
      lives: LIVES,
      easy: EASY,
      controls: MOVE,
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' 위에서 떨어지는 ' + W(o) + jo(o.ko, '을를') + ' 피해요'; },
      storyEn: function (h, o) { return E(h.en) + ' dodging falling ' + E(o.en); },
      music: { en: 'Bright chiptune with warm synth', ko: '밝은 8비트 게임 음악과 따뜻한 신스', bpm: 110 }
    },
    {
      id: 'run', ko: '러닝 점프',
      rule: function (h, o) { return '화면이 저절로 흐르고, 오른쪽에서 다가오는 ' + W(o) + jo(o.ko, '을를') + ' 점프해서 넘어요.'; },
      hero: function (h) { return W(h) + '. 화면 왼쪽 아래에서 달려요.'; },
      obstacle: function (o) { return W(o) + '. 간격은 넓게, 속도는 천천히 해 줘.'; },
      score: '1초에 20점. 300점(약 15초)이 되면 클리어예요.',
      lives: LIVES,
      easy: EASY,
      controls: ['키보드 스페이스나 ↑로 점프', '화면 아래 점프 버튼', '게임 화면 아무 곳이나 탭하면 점프'],
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' 달리면서 ' + W(o) + jo(o.ko, '을를') + ' 뛰어넘어요'; },
      storyEn: function (h, o) { return E(h.en) + ' running and jumping over ' + E(o.en); },
      music: { en: 'Upbeat 8-bit running theme', ko: '신나는 8비트 달리기 음악', bpm: 125 }
    },
    {
      id: 'breakout', ko: '벽돌깨기',
      rule: function (h, o) { return '넓은 받침대로 공을 튕겨서 위쪽의 ' + W(o) + ' 벽돌을 깨요. 공은 너무 빠르지 않게 해 줘.'; },
      hero: function (h) { return W(h) + '. 화면 아래에서 공을 받아 치는 넓은 받침대가 돼요.'; },
      obstacle: function (o) { return W(o) + ' 모양 벽돌. 화면 위쪽에 1~2줄로 크게 놓아요.'; },
      score: '벽돌 하나에 100점. 3개를 깨면 300점으로 클리어예요.',
      lives: '5개. 공을 놓치면 목숨이 하나 줄고 받침대 위에서 다시 시작해요. 다 잃으면 게임 오버 화면과 다시 하기 버튼을 보여 줘.',
      easy: '처음 하는 사람도 끝까지 갈 수 있게 쉽게 만들어 줘. 받침대가 공을 받는 판정은 넉넉하게 잡아 줘.',
      controls: ['키보드 ←, →', '화면 아래 왼쪽·오른쪽 버튼(누르고 있으면 계속 움직여요)', '게임 화면을 손가락이나 마우스로 끌면 받침대가 따라와요'],
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' 공을 튕겨 ' + W(o) + ' 벽돌을 깨요'; },
      storyEn: function (h, o) { return E(h.en) + ' bouncing a ball to break ' + E(o.one + '-shaped bricks'); },
      music: { en: 'Playful bouncy arcade chiptune', ko: '통통 튀는 8비트 오락실 음악', bpm: 115 }
    },
    {
      id: 'catch', ko: '받아먹기',
      rule: function (h, o) { return '위에서 떨어지는 별을 받으면 점수가 오르고, ' + W(o) + jo(o.ko, '은는') + ' 피해요.'; },
      hero: function (h) { return W(h) + '. 화면 맨 아래에서 좌우로 움직여요.'; },
      obstacle: function (o) { return W(o) + '. 별 사이에 가끔 섞여서 천천히 떨어져요.'; },
      score: '별 하나에 30점. 10개를 받으면 300점으로 클리어예요.',
      lives: LIVES,
      easy: '처음 하는 사람도 끝까지 갈 수 있게 쉽게 만들어 줘. 별을 받는 판정은 넉넉하게, 장애물 부딪힘 판정은 그림보다 작게 잡아 줘.',
      controls: MOVE,
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' 떨어지는 별을 받고 ' + W(o) + jo(o.ko, '은는') + ' 피해요'; },
      storyEn: function (h, o) { return E(h.en) + ' catching falling stars and avoiding ' + E(o.en); },
      music: { en: 'Happy bouncy chiptune with light bells', ko: '경쾌한 8비트 게임 음악과 맑은 종소리', bpm: 105 }
    },
    {
      id: 'fly', ko: '날아가기',
      rule: function (h, o) { return '누르면 위로 날아오르고, 떼면 천천히 내려와요. 오른쪽에서 오는 ' + W(o) + ' 기둥 사이의 넓은 빈틈으로 지나가요.'; },
      hero: function (h) { return W(h) + '. 화면 왼쪽에서 날아요.'; },
      obstacle: function (o) { return W(o) + jo(o.ko, '으로') + ' 쌓은 기둥. 빈틈은 넓게, 속도는 천천히 하고, 시작하고 3초 동안은 기둥이 나오지 않게 해 줘.'; },
      score: '기둥 하나를 지날 때마다 50점. 6개를 지나면 300점으로 클리어예요.',
      lives: '5개. 천장, 바닥, 기둥에 닿으면 목숨이 하나 줄고 1.5초 동안 깜빡이며 무적이에요. 다 잃으면 게임 오버 화면과 다시 하기 버튼을 보여 줘.',
      easy: EASY,
      controls: ['키보드 스페이스나 ↑', '화면 아래 날기 버튼', '게임 화면 아무 곳이나 탭'],
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' ' + W(o) + ' 기둥 사이로 날아가요'; },
      storyEn: function (h, o) { return E(h.en) + ' flying through gaps between towers of ' + E(o.en); },
      music: { en: 'Light airy chiptune with soft synth pads', ko: '가볍고 시원한 8비트 게임 음악', bpm: 100 }
    },
    {
      id: 'shoot', ko: '슈팅',
      rule: function (h, o) { return '주인공이 좌우로 움직이며 저절로 위로 쏘고, 위에서 내려오는 ' + W(o) + jo(o.ko, '을를') + ' 맞혀요.'; },
      hero: function (h) { return W(h) + '. 화면 맨 아래에서 좌우로 움직이고, 쏘는 것은 저절로 해요.'; },
      obstacle: function (o) { return W(o) + '. 위에서 천천히 내려오고, 바닥에 닿으면 그냥 사라져요.'; },
      score: '하나 맞힐 때마다 20점. 15개를 맞히면 300점으로 클리어예요.',
      lives: '5개. 장애물과 부딪히면 하나 줄고 1.5초 동안 깜빡이며 무적이에요. 다 잃으면 게임 오버 화면과 다시 하기 버튼을 보여 줘.',
      easy: '처음 하는 사람도 끝까지 갈 수 있게 쉽게 만들어 줘. 맞히는 판정은 넉넉하게, 부딪힘 판정은 그림보다 작게 잡아 줘.',
      controls: MOVE,
      storyKo: function (h, o) { return W(h) + jo(h.ko, '이가') + ' 내려오는 ' + W(o) + jo(o.ko, '을를') + ' 쏘아 맞혀요'; },
      storyEn: function (h, o) { return E(h.en) + ' shooting at ' + E(o.en) + ' coming down from the sky'; },
      music: { en: 'Energetic retro arcade chiptune', ko: '힘찬 8비트 오락실 음악', bpm: 130 }
    }
  ];

  var FILES = { html: 'index.html', poster: 'poster.png', music: 'music.mp3', ending: 'ending.mp4' };
  var FOLDER = 'my-game';
  var SETS = [
    { id: 'bright', ko: '밝은' },
    { id: 'space', ko: '우주' },
    { id: 'forest', ko: '숲' }
  ];
  var DEFAULT = { genre: 'dodge', hero: 'rabbit', obstacle: 'carrot', idea: '' };
  var IDEA_MAX = 120;

  function find(list, id) { for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i]; return null; }
  function cleanIdea(s) {
    return String(s == null ? '' : s).replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, IDEA_MAX);
  }
  function normalize(c) {
    c = c || {};
    return {
      genre: find(GENRES, c.genre) ? c.genre : DEFAULT.genre,
      hero: find(HEROES, c.hero) ? c.hero : DEFAULT.hero,
      obstacle: find(OBSTACLES, c.obstacle) ? c.obstacle : DEFAULT.obstacle,
      idea: cleanIdea(c.idea)
    };
  }
  function parts(choice) {
    var c = normalize(choice || state);
    return { c: c, g: find(GENRES, c.genre), h: find(HEROES, c.hero), o: find(OBSTACLES, c.obstacle), idea: c.idea };
  }

  /* ---------- 상태(고른 값) ---------- */

  var STORE = 'gamekit-choice-v1';
  var state = (function () {
    try { return normalize(JSON.parse(localStorage.getItem(STORE) || 'null')); } catch (e) { return normalize(DEFAULT); }
  })();
  var listeners = [];
  function getChoice() { return { genre: state.genre, hero: state.hero, obstacle: state.obstacle, idea: state.idea }; }
  function setChoice(partial) {
    var next = normalize(Object.assign({}, state, partial || {}));
    var changed = Object.keys(next).filter(function (k) { return next[k] !== state[k]; });
    if (!changed.length) return getChoice();
    state = next;
    try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* 기억만 안 돼요 */ }
    var snap = getChoice();
    listeners.slice().forEach(function (fn) { try { fn(snap, changed); } catch (e) { setTimeout(function () { throw e; }); } });
    try { document.dispatchEvent(new CustomEvent('gamekit:change', { detail: { choice: snap, changed: changed } })); } catch (e) { /* 오래된 브라우저 */ }
    return snap;
  }
  function subscribe(fn) {
    listeners.push(fn);
    return function () { listeners = listeners.filter(function (f) { return f !== fn; }); };
  }

  /* ---------- 글 만들기 (표지 포함 버전) ---------- */

  function storyKo(choice) { var p = parts(choice); return p.g.storyKo(p.h, p.o); }
  function storyEn(choice) { var p = parts(choice); return p.g.storyEn(p.h, p.o); }
  function label(choice) { var p = parts(choice); return p.g.ko + ' · ' + p.h.ko + ' · ' + p.o.ko; }

  function gameMarked(choice) {
    var p = parts(choice), g = p.g, h = p.h, o = p.o;
    var L = [
      'HTML 파일 하나로 웹 미니게임을 만들어 줘. CSS와 JS도 그 파일 안에 넣어 줘.',
      '이 폴더에 index.html로 저장해 줘.',
      '',
      '[게임]',
      '- 장르: ' + hl(g.ko) + '. ' + g.rule(h, o),
      '- 주인공: ' + g.hero(h),
      '- 장애물: ' + g.obstacle(o),
      '- 점수: ' + g.score,
      '- 목숨: ' + g.lives,
      '- ' + (g.easy || EASY)
    ];
    if (p.idea) L.push('- 내 아이디어: ' + hl(p.idea) + ' (고른 것과 다르면 내 아이디어를 먼저 따라 줘.)');
    L.push('', '[조작] 세 가지 모두 되게 해 줘.');
    g.controls.forEach(function (x) { L.push('- ' + x); });
    L.push(
      '',
      '[화면]',
      '- 휴대폰 세로 화면(폭 390px)에서도 가로 스크롤 없이 다 보이고, 버튼이 화면 안에 있어야 해.',
      '- 점수와 목숨을 크게 보여 줘.',
      '- 주인공과 장애물은 캔버스 도형으로 그려 줘. 이모지, 인터넷 그림, 바깥 글꼴, 외부 라이브러리는 쓰지 마.',
      '',
      '[미디어 파일] 나중에 index.html과 같은 폴더에 넣을 거야.',
      '- poster.png: 시작 화면에 크게 보여 주고, 아래에 시작 버튼을 둬.',
      '- music.mp3: 시작 버튼을 누른 뒤에 반복 재생해 줘. 음악 끄기·켜기 버튼도 넣어 줘.',
      '- ending.mp4: 클리어하면 화면을 덮어서 재생하고, 끝나면 다시 하기 버튼을 보여 줘.',
      '- 경로는 파일 이름 그대로 써 줘. 앞에 / 나 폴더 이름을 붙이지 마.',
      '- 지금은 세 파일이 없어. 파일이 없거나 재생이 막혀도 오류 없이 그 기능만 건너뛰고 게임은 계속돼야 해.',
      '- fetch로 파일을 미리 확인하지 말고, img·audio·video 요소의 error 이벤트와 play()의 catch로 처리해 줘. 내 컴퓨터에서 파일을 더블클릭해서 열어도 돼야 해.',
      '',
      '다 하면 만든 파일과 확인한 것을 알려 줘.'
    );
    return L.join('\n');
  }

  // 발표용 짧은 보기: 바꿀 곳 네 줄만 보여 줘요. 복사는 전문을 해요.
  function gameShortMarked(choice) {
    var p = parts(choice);
    var L = [
      '장르  ' + hl(p.g.ko),
      '주인공  ' + hl(p.h.ko),
      '장애물  ' + hl(p.o.ko),
      p.g.storyKo(p.h, p.o) + '. ' + p.g.score
    ];
    if (p.idea) L.splice(3, 0, '내 아이디어  ' + hl(p.idea));
    return L.join('\n');
  }

  function ideaLine(p) { return p.idea ? '\n내 아이디어: ' + hl(p.idea) : ''; }

  function mediaMarked(choice) {
    var p = parts(choice), g = p.g, h = p.h, o = p.o;
    var sKo = g.storyKo(h, o), sEn = g.storyEn(h, o);
    return {
      poster: {
        ask: '방금 만든 게임의 시작 화면 포스터를 무료 그림 생성 사이트에서 만들려고 해.\n' +
          '게임: ' + sKo + '.' + ideaLine(p) + '\n' +
          '이 게임의 주인공, 장애물, 색에 맞춰서 그림 생성용 영어 프롬프트를 4줄 안쪽으로 써 줘.\n' +
          '조건: 가로 16:9, 밝은 만화풍, 글자·로고·워터마크 없음, 사진 아님.\n' +
          '복사하기 좋게 코드 블록 하나에 프롬프트만 넣어 줘.',
        en: 'Opening poster for a simple web mini-game: ' + sEn + '.\n' +
          'Bright cartoon illustration, thick clean outlines, cheerful colors, simple background.\n' +
          'Big ' + E(h.one) + ' in the center, ' + E(o.en) + ' around it.\n' +
          '16:9 landscape, no text, no letters, no logo, no watermark, not a photo.',
        ko: '웹 미니게임의 시작 화면 포스터예요. ' + sKo + '.\n' +
          '밝은 만화풍 그림, 굵고 깔끔한 테두리, 밝은 색, 단순한 배경.\n' +
          '가운데에 ' + W(h) + jo(h.ko, '을를') + ' 크게, 주변에 ' + W(o) + '.\n' +
          '가로 16:9, 글자·로고·워터마크 없이, 사진이 아닌 그림으로.' + ideaLine(p)
      },
      music: {
        ask: '방금 만든 게임에 넣을 배경 음악을 무료 음악 생성 사이트에서 만들려고 해.\n' +
          '게임: ' + sKo + '.' + ideaLine(p) + '\n' +
          '이 게임 분위기에 맞는 음악 생성용 영어 프롬프트를 4줄 안쪽으로 써 줘.\n' +
          '조건: 가사와 목소리 없이 악기만, 15초 안팎, 끝과 처음이 이어지는 반복용, 밝은 8비트 게임 음악.\n' +
          '복사하기 좋게 코드 블록 하나에 프롬프트만 넣어 줘.',
        en: 'Instrumental only. No vocals, no lyrics, no voice.\n' +
          '15-second seamless loop for a web mini-game: ' + sEn + '.\n' +
          g.music.en + ', about ' + g.music.bpm + ' BPM, same energy from start to end.\n' +
          'Perfect loop: no fade in, no fade out, no silence at the end.',
        ko: '목소리와 가사 없이 악기만 써요.\n' +
          '웹 미니게임에서 반복할 15초 배경 음악이에요. ' + sKo + '.\n' +
          g.music.ko + ', 빠르기 약 ' + g.music.bpm + 'BPM, 처음부터 끝까지 같은 느낌.\n' +
          '끝과 처음이 자연스럽게 이어지게, 서서히 커지거나 작아지지 않게, 끝에 조용한 부분 없이.' + ideaLine(p)
      },
      video: {
        ask: '방금 만든 게임의 클리어 화면에 넣을 5초 영상을 무료 영상 생성 사이트에서 만들려고 해.\n' +
          '포스터 그림을 올려서 영상으로 바꾸는 방식(image-to-video)이야.\n' +
          '게임: ' + sKo + '.' + ideaLine(p) + '\n' +
          '이긴 순간을 축하하는 장면으로 영상 생성용 영어 프롬프트를 4줄 안쪽으로 써 줘.\n' +
          '조건: 5초, 포스터와 같은 캐릭터와 색, 글자·자막·로고·워터마크 없음.\n' +
          '복사하기 좋게 코드 블록 하나에 프롬프트만 넣어 줘.',
        en: '5-second victory video, image-to-video from the uploaded poster.\n' +
          sEn + ', and the ' + E(h.one) + ' has just won the game.\n' +
          'Slow camera push-in, confetti, bright and cheerful.\n' +
          'Keep the same character, colors and composition as the poster.\n' +
          'No text, no subtitles, no logo, no watermark.',
        ko: '올린 포스터 그림으로 만드는 5초 축하 영상이에요.\n' +
          sKo + '. 방금 게임을 이겼어요.\n' +
          '카메라가 천천히 다가가고, 색종이가 터지고, 밝고 신나는 분위기예요.\n' +
          '포스터와 같은 캐릭터, 같은 색, 같은 구도로.\n' +
          '글자·자막·로고·워터마크 없이.' + ideaLine(p)
      }
    };
  }

  function mergeMarked(choice) {
    var p = parts(choice);
    return [
      '방금 만든 게임 HTML을 고쳐 줘. 게임은 "' + p.g.storyKo(p.h, p.o) + '"예요.',
      FOLDER + ' 폴더에 index.html과 함께 아래 세 파일을 넣었어.',
      '- poster.png: 시작 화면 포스터',
      '- music.mp3: 배경 음악',
      '- ending.mp4: 클리어 영상',
      '',
      '이렇게 고쳐 줘.',
      '1. 시작 화면에 poster.png를 화면에 맞게 크게 보여 주고, 아래에 시작 버튼을 둬.',
      '2. 시작 버튼을 누르면 music.mp3를 반복 재생해. 음악 끄기·켜기 버튼도 둬.',
      '3. 클리어하면 ending.mp4를 화면을 덮어서 재생하고, 끝나면 다시 하기 버튼을 보여 줘.',
      '4. 경로는 같은 폴더의 파일 이름 그대로 써 줘. 대소문자도 그대로야.',
      '5. 파일이 없거나 재생이 막혀도 게임은 멈추지 말고 그 기능만 건너뛰어 줘. fetch로 미리 확인하지 말고, 요소의 error 이벤트와 play()의 catch로 처리해 줘. 파일을 더블클릭해서 열어도 돼야 해.',
      '6. 게임 규칙과 조작은 바꾸지 마.',
      '다 고치면 이 폴더의 index.html에 바로 저장해 줘.'
    ].join('\n');
  }

  function textMarked(kind, variant, choice, view) {
    if (kind === 'game') return view === 'short' ? gameShortMarked(choice) : gameMarked(choice);
    if (kind === 'merge') return mergeMarked(choice);
    var m = mediaMarked(choice)[kind];
    if (!m) throw new Error('GameKit: 모르는 프롬프트 종류예요: ' + kind);
    return m[variant] || m.ask;
  }

  /* ---------- 밖으로 주는 글 (표지 없는 버전) ---------- */

  function buildPrompt(choice) { return strip(gameMarked(choice)); }
  function mediaPrompts(choice) {
    var m = mediaMarked(choice), out = {};
    Object.keys(m).forEach(function (k) { out[k] = { ask: strip(m[k].ask), en: strip(m[k].en), ko: strip(m[k].ko) }; });
    return out;
  }
  function mergePrompt(choice) { return strip(mergeMarked(choice)); }
  function text(kind, variant, choice) { return strip(textMarked(kind, variant, choice)); }

  // 미리 만든 묶음 중 고른 게임과 어울리는 세트를 골라요(추천 표시용).
  function suggestSet(choice) {
    var c = normalize(choice || state);
    if (c.hero === 'ship' || c.hero === 'robot' || c.obstacle === 'meteor') return 'space';
    if (['carrot', 'cactus', 'bug', 'cloud'].indexOf(c.obstacle) >= 0 || ['rabbit', 'dino', 'elephant', 'puppy'].indexOf(c.hero) >= 0) return 'forest';
    return 'bright';
  }

  /* ---------- 복사 ---------- */

  function selectContents(el) {
    try {
      if (!el) return false;
      if (typeof el.select === 'function') { el.focus({ preventScroll: true }); el.select(); return true; }
      var r = document.createRange();
      r.selectNodeContents(el);
      var s = window.getSelection();
      s.removeAllRanges();
      s.addRange(r);
      if (el.focus) el.focus({ preventScroll: true });
      return true;
    } catch (e) { return false; }
  }

  // 'copied' | 'selected' | 'failed'를 돌려줘요. 클립보드가 막히면 예전 방법을 한 번 더 쓰고, 그래도 안 되면 글을 선택해 둬요.
  function copyText(value, selectEl) {
    var t = String(value);
    function legacy() {
      var ok = false, ta = null, active = document.activeElement;
      try {
        ta = document.createElement('textarea');
        ta.value = t;
        ta.setAttribute('readonly', '');
        ta.setAttribute('aria-hidden', 'true');
        ta.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:1px;padding:0;border:0;opacity:0;pointer-events:none;';
        document.body.appendChild(ta);
        ta.focus({ preventScroll: true });
        ta.select();
        ok = document.execCommand && document.execCommand('copy');
      } catch (e) { ok = false; }
      if (ta && ta.parentNode) ta.parentNode.removeChild(ta);
      try { if (active && active.focus) active.focus({ preventScroll: true }); } catch (e) { /* 그대로 둬요 */ }
      if (ok) return 'copied';
      return selectContents(selectEl) ? 'selected' : 'failed';
    }
    try {
      if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext !== false) {
        return navigator.clipboard.writeText(t).then(function () { return 'copied'; }, legacy);
      }
    } catch (e) { /* 아래 예전 방법으로 */ }
    return Promise.resolve(legacy());
  }

  var COPY_SAY = {
    copied: '복사했어요. Claude 입력창에 붙여 넣어요.',
    selected: '글을 선택해 뒀어요. Ctrl+C(맥은 Cmd+C)를 눌러 복사해요.',
    failed: '복사가 막혔어요. 글을 끌어서 선택한 뒤 복사해요.'
  };

  /* ---------- 화면 부품 ---------- */

  var CSS = [
    '.gk-picker,.gk-box{color:var(--gk-ink,#141414);-webkit-text-size-adjust:100%}',
    '.gk-picker *,.gk-box *{box-sizing:border-box}',
    '.gk-picker{display:grid;gap:1.1em;min-width:0}',
    '.gk-rows{display:grid;gap:.85em;min-width:0}',
    '.gk-row{display:grid;grid-template-columns:6.2em minmax(0,1fr);align-items:start;gap:.45em .8em;min-width:0}',
    '.gk-label{font-size:.875em;font-weight:700;color:var(--gk-muted,#6b6b6b);padding-top:.7em;line-height:1.3}',
    '.gk-opts{display:flex;flex-wrap:wrap;gap:.45em;min-width:0}',
    '.gk-opt,.gk-btn,.gk-tab{-webkit-appearance:none;appearance:none;font:inherit;line-height:1.2;cursor:pointer;border-radius:999px;margin:0;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;gap:.4em;touch-action:manipulation;-webkit-tap-highlight-color:transparent}',
    '.gk-opt{font-size:.9375em;font-weight:600;padding:.55em 1em;min-height:2.6em;border:1.5px solid var(--gk-line,#d9d9d9);background:var(--gk-surface,#fff);color:var(--gk-ink,#141414);transition:background-color .15s,border-color .15s,transform .1s}',
    '.gk-opt:hover{border-color:var(--gk-accent,#ff6f0f)}',
    '.gk-opt:active{transform:scale(.97)}',
    '.gk-opt[aria-pressed="true"]{background:var(--gk-accent,#ff6f0f);border-color:var(--gk-accent,#ff6f0f);color:var(--gk-on-accent,#141414);font-weight:700}',
    '.gk-idea-wrap{display:flex;gap:.45em;min-width:0}',
    '.gk-idea{flex:1;min-width:0;font:inherit;font-size:.9375em;padding:.6em .9em;min-height:2.6em;border-radius:.7em;border:1.5px solid var(--gk-line,#d9d9d9);background:var(--gk-surface,#fff);color:var(--gk-ink,#141414)}',
    '.gk-idea::placeholder{color:var(--gk-muted,#6b6b6b);opacity:1}',
    '.gk-btn{font-size:.9375em;font-weight:700;padding:.55em 1.05em;min-height:2.6em;border:1.5px solid var(--gk-line,#d9d9d9);background:var(--gk-surface,#fff);color:var(--gk-ink,#141414);white-space:nowrap}',
    '.gk-btn:hover{border-color:var(--gk-ink,#141414)}',
    '.gk-btn.gk-primary{background:var(--gk-accent,#ff6f0f);border-color:var(--gk-accent,#ff6f0f);color:var(--gk-on-accent,#141414)}',
    '.gk-btn.gk-primary:hover{filter:brightness(.95)}',
    '.gk-btn img{width:1.15em;height:1.15em;object-fit:contain;flex:none}',
    '.gk-tools{display:flex;flex-wrap:wrap;align-items:center;gap:.5em .8em;padding-left:7em}',
    '.gk-summary{font-size:.875em;color:var(--gk-muted,#6b6b6b)}',
    '.gk-summary b{color:var(--gk-ink,#141414)}',
    '.gk-box{border:1.5px solid var(--gk-line,#d9d9d9);border-radius:1em;background:var(--gk-sunk,#f7f7f5);overflow:hidden;min-width:0}',
    '.gk-head{display:flex;flex-wrap:wrap;align-items:center;gap:.5em .6em;padding:.65em .75em .65em 1em;border-bottom:1px solid var(--gk-line,#d9d9d9);background:var(--gk-surface,#fff)}',
    '.gk-title{font-weight:700;font-size:.9375em;margin-right:auto}',
    '.gk-tabs{display:inline-flex;flex-wrap:wrap;gap:.3em;padding:.2em;border-radius:999px;background:var(--gk-sunk,#f2f2f0)}',
    '.gk-tab{font-size:.8125em;font-weight:700;padding:.45em .85em;min-height:2.4em;border:0;background:transparent;color:var(--gk-muted,#6b6b6b)}',
    '.gk-tab[aria-pressed="true"]{background:var(--gk-ink,#141414);color:var(--gk-surface,#fff)}',
    '.gk-status{margin:0;padding:.55em 1.1em;font-size:.8125em;font-weight:600;line-height:1.45;color:var(--gk-ok,#0b7a5e);background:var(--gk-surface,#fff);border-bottom:1px solid var(--gk-line,#d9d9d9)}',
    '.gk-status:empty{padding:0;border:0}',
    '.gk-status.gk-warn{color:var(--gk-warn,#9a4b00)}',
    '.gk-text{margin:0;padding:1em 1.1em;font:inherit;font-size:.9375em;line-height:1.65;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere;color:var(--gk-body,#2b2b2b);max-height:24em;overflow:auto;outline-offset:-3px}',
    '.gk-short .gk-text{max-height:none}',
    '.gk-hl{background:var(--gk-mark,#ffe2c7);color:var(--gk-mark-ink,inherit);border-radius:.25em;padding:0 .1em;font-weight:700;-webkit-box-decoration-break:clone;box-decoration-break:clone}',
    '.gk-changed .gk-hl{animation:gk-flash .9s ease-out}',
    '@keyframes gk-flash{from{background:var(--gk-accent,#ff6f0f);color:var(--gk-on-accent,#141414)}}',
    '.gk-note{margin:0;padding:0 1.1em .9em;font-size:.8125em;line-height:1.5;color:var(--gk-muted,#6b6b6b)}',
    '.gk-picker :focus-visible,.gk-box :focus-visible{outline:3px solid var(--gk-focus,#0b57d0);outline-offset:2px}',
    '@media (max-width:560px){.gk-row{grid-template-columns:minmax(0,1fr)}.gk-label{padding-top:0}.gk-tools{padding-left:0}' +
      '.gk-tabs{order:3;flex:1 1 100%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr))}.gk-tab{padding:.45em .3em}' +
      '.gk-head a.gk-btn{order:4;flex:1 1 100%}}',
    '@media (prefers-reduced-motion:reduce){.gk-changed .gk-hl{animation:none}.gk-opt{transition:none}}'
  ].join('\n');

  function injectCss() {
    if (document.getElementById('gk-style')) return;
    var s = document.createElement('style');
    s.id = 'gk-style';
    s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v == null || v === false) return;
      if (k === 'text') n.textContent = v;
      else if (k === 'class') n.className = v;
      else n.setAttribute(k, v === true ? '' : v);
    });
    (kids || []).forEach(function (k) { if (k) n.appendChild(typeof k === 'string' ? document.createTextNode(k) : k); });
    return n;
  }

  // 표지가 든 글을 글자 노드와 <mark>로 바꿔 넣어요. 사용자 글은 textContent로만 넣어요.
  function renderMarked(target, marked) {
    while (target.firstChild) target.removeChild(target.firstChild);
    var re = /\u0001([^\u0001\u0002]*)\u0002/g, last = 0, m;
    while ((m = re.exec(marked))) {
      if (m.index > last) target.appendChild(document.createTextNode(marked.slice(last, m.index)));
      target.appendChild(el('mark', { class: 'gk-hl', text: m[1] }));
      last = re.lastIndex;
    }
    if (last < marked.length) target.appendChild(document.createTextNode(marked.slice(last)));
  }

  function isShown(node) {
    try {
      if (node.checkVisibility) return node.checkVisibility({ visibilityProperty: true, opacityProperty: false });
      return !!(node.offsetWidth || node.offsetHeight);
    } catch (e) { return true; }
  }

  // 발표 엔진(scene.js)은 창 전체에서 키를 받아 장면을 넘겨요. 부품 안에서 친 키가 장면을 넘기지 않게 여기서 멈춰요.
  // 입력칸: 글 치는 키는 모두 멈추고, PageUp·PageDown(발표 리모컨)과 Esc만 보내요.
  // 버튼: Enter와 스페이스(누르기)만 멈춰요. 화살표는 그대로 보내서 리모컨으로 장면을 넘길 수 있어요.
  function guardKeys(root) {
    root.addEventListener('keydown', function (e) {
      var t = e.target;
      if (!t || t === root || !t.matches) return;
      if (t.matches('input, textarea, [contenteditable]')) {
        if (!isShown(t)) { t.blur(); return; }
        if (e.key === 'Escape') { t.blur(); return; }
        if (e.key === 'PageUp' || e.key === 'PageDown') return;
        e.stopPropagation();
      } else if (t.matches('button, a, select, [tabindex]')) {
        if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') e.stopPropagation();
      }
    });
  }

  var uid = 0;
  var TITLES = { game: '게임 프롬프트', poster: '포스터 프롬프트', music: '음악 프롬프트', video: '영상 프롬프트', merge: '합치기 프롬프트' };
  var VARIANTS = [
    { id: 'ask', ko: 'Claude에게' },
    { id: 'en', ko: '영어로 바로' },
    { id: 'ko', ko: '한국어로 바로' }
  ];

  // 프롬프트 상자 하나(머리줄, 복사, 글). mount와 mountPrompt가 같이 써요.
  function buildBox(opts) {
    var kind = opts.kind || 'game';
    var hasTabs = opts.tabs !== false && (kind === 'poster' || kind === 'music' || kind === 'video');
    var variant = opts.variant || 'ask';
    var id = 'gk' + (++uid);
    var box = el('div', { class: 'gk-box' + (opts.view === 'short' ? ' gk-short' : ''), 'data-kind': kind });
    var head = el('div', { class: 'gk-head' });
    var title = el('span', { class: 'gk-title', id: id + '-t', text: opts.title || TITLES[kind] || '프롬프트' });
    head.appendChild(title);
    var tabs = null;
    if (hasTabs) {
      tabs = el('div', { class: 'gk-tabs', role: 'group', 'aria-label': '프롬프트 종류' });
      VARIANTS.forEach(function (v) {
        tabs.appendChild(el('button', { type: 'button', class: 'gk-tab', 'data-variant': v.id, 'aria-pressed': String(v.id === variant), text: v.ko }));
      });
      head.appendChild(tabs);
    }
    var copyBtn = null;
    if (opts.copy !== false) {
      copyBtn = el('button', { type: 'button', class: 'gk-btn gk-primary gk-copy', 'aria-describedby': id + '-t', text: opts.copyText || '복사' });
      head.appendChild(copyBtn);
    }
    (opts.links || []).forEach(function (l) {
      if (!l || !/^https?:\/\//.test(String(l.href))) return;
      var a = el('a', { class: 'gk-btn' + (l.primary ? ' gk-primary' : ''), href: l.href, target: '_blank', rel: 'noopener noreferrer' });
      if (l.icon) a.appendChild(el('img', { src: l.icon, alt: '' }));
      a.appendChild(document.createTextNode(l.text || '열기'));
      head.appendChild(a);
    });
    var status = el('p', { class: 'gk-status', role: 'status', 'aria-live': 'polite' });
    box.appendChild(head);
    box.appendChild(status);
    var pre = el('pre', { class: 'gk-text', tabindex: '0', 'aria-labelledby': id + '-t' });
    box.appendChild(pre);
    var note = el('p', { class: 'gk-note', hidden: true });
    box.appendChild(note);

    var statusTimer = 0, lastMarked = null;
    function say(msg, warn) {
      clearTimeout(statusTimer);
      status.textContent = msg;
      status.classList.toggle('gk-warn', !!warn);
      if (msg) statusTimer = setTimeout(function () { status.textContent = ''; }, warn ? 9000 : 4500);
    }
    function render(flash) {
      var c = getChoice();
      var marked = textMarked(kind, variant, c, opts.view);
      if (marked !== lastMarked) {
        renderMarked(pre, marked);
        if (flash && lastMarked !== null) {
          box.classList.remove('gk-changed');
          void box.offsetWidth; // 애니메이션을 다시 시작해요
          box.classList.add('gk-changed');
        }
        lastMarked = marked;
      }
      var showNote = hasTabs && variant === 'en' && !!c.idea;
      note.hidden = !showNote;
      note.textContent = showNote ? '내 아이디어는 영어 프롬프트에 들어가지 않아요. \'Claude에게\'를 고르면 같이 넣어서 써 줘요.' : '';
    }
    if (tabs) tabs.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.gk-tab') : null;
      if (!b) return;
      variant = b.getAttribute('data-variant');
      tabs.querySelectorAll('.gk-tab').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      render(true);
    });
    if (copyBtn) copyBtn.addEventListener('click', function () {
      var plain = strip(textMarked(kind, variant, getChoice(), 'full'));
      copyText(plain, pre).then(function (r) {
        say(COPY_SAY[r], r !== 'copied');
        try { document.dispatchEvent(new CustomEvent('gamekit:copy', { detail: { kind: kind, variant: hasTabs ? variant : null, result: r } })); } catch (e) { /* 그대로 둬요 */ }
      });
    });
    var off = subscribe(function () { render(true); });
    render(false);
    return {
      el: box,
      getVariant: function () { return variant; },
      setVariant: function (v) { if (!hasTabs) return; var b = tabs.querySelector('[data-variant="' + v + '"]'); if (b) b.click(); },
      text: function () { return strip(textMarked(kind, variant, getChoice(), 'full')); },
      destroy: function () { off(); clearTimeout(statusTimer); if (box.parentNode) box.parentNode.removeChild(box); }
    };
  }

  function prepRoot(root) {
    if (!root || root.nodeType !== 1) throw new Error('GameKit: 그릴 자리(요소)를 주세요.');
    injectCss();
    root.classList.add('no-advance'); // 발표 엔진이 이 안의 클릭으로 장면을 넘기지 않아요
    if (!root.__gkGuard) { guardKeys(root); root.__gkGuard = true; }
  }

  // 고르기 + 프롬프트 상자를 그려요.
  function mount(root, opts) {
    opts = opts || {};
    prepRoot(root);
    var view = opts.view === 'short' ? 'short' : 'full';
    var id = 'gk' + (++uid);
    var wrap = el('div', { class: 'gk-picker gk-' + view });
    var rows = el('div', { class: 'gk-rows' });
    var groups = [
      { key: 'genre', ko: '장르', list: GENRES },
      { key: 'hero', ko: '주인공', list: HEROES },
      { key: 'obstacle', ko: '장애물', list: OBSTACLES }
    ];
    groups.forEach(function (gr) {
      var lid = id + '-' + gr.key;
      var row = el('div', { class: 'gk-row', role: 'group', 'aria-labelledby': lid });
      row.appendChild(el('span', { class: 'gk-label', id: lid, text: gr.ko }));
      var opt = el('div', { class: 'gk-opts' });
      gr.list.forEach(function (it) {
        opt.appendChild(el('button', { type: 'button', class: 'gk-opt', 'data-k': gr.key, 'data-v': it.id, 'aria-pressed': 'false', text: it.ko }));
      });
      row.appendChild(opt);
      rows.appendChild(row);
    });
    var ideaInput = null, clearBtn = null;
    if (opts.idea !== false) {
      var iid = id + '-idea';
      var irow = el('div', { class: 'gk-row gk-idea-row' });
      irow.appendChild(el('label', { class: 'gk-label', for: iid, text: '내 아이디어' }));
      var iw = el('div', { class: 'gk-idea-wrap' });
      ideaInput = el('input', { id: iid, class: 'gk-idea', type: 'text', maxlength: String(IDEA_MAX), autocomplete: 'off', spellcheck: 'false', placeholder: opts.ideaPlaceholder || '예: 점수가 오를수록 빨라져요' });
      clearBtn = el('button', { type: 'button', class: 'gk-btn gk-clear', text: '지우기' });
      iw.appendChild(ideaInput);
      iw.appendChild(clearBtn);
      irow.appendChild(iw);
      rows.appendChild(irow);
    }
    var tools = el('div', { class: 'gk-tools' });
    var randomBtn = null;
    if (opts.random !== false) {
      randomBtn = el('button', { type: 'button', class: 'gk-btn gk-random', text: '아무거나' });
      tools.appendChild(randomBtn);
    }
    var summary = el('span', { class: 'gk-summary', 'aria-live': 'polite' });
    tools.appendChild(summary);
    rows.appendChild(tools);
    wrap.appendChild(rows);

    var boxCtl = null;
    if (opts.prompt !== false) {
      boxCtl = buildBox({ kind: 'game', view: view, title: opts.title, copy: opts.copy, links: opts.links, copyText: opts.copyLabel });
      wrap.appendChild(boxCtl.el);
    }
    root.appendChild(wrap);

    function sync() {
      var c = getChoice();
      wrap.querySelectorAll('.gk-opt').forEach(function (b) {
        b.setAttribute('aria-pressed', String(c[b.getAttribute('data-k')] === b.getAttribute('data-v')));
      });
      if (ideaInput && document.activeElement !== ideaInput && ideaInput.value !== c.idea) ideaInput.value = c.idea;
      if (clearBtn) clearBtn.hidden = !(ideaInput && ideaInput.value);
      summary.textContent = '';
      summary.appendChild(document.createTextNode('지금: '));
      summary.appendChild(el('b', { text: label(c) }));
      if (c.idea) summary.appendChild(document.createTextNode(' + 내 아이디어'));
    }

    wrap.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.gk-opt') : null;
      if (!b || !wrap.contains(b)) return;
      var patch = {};
      patch[b.getAttribute('data-k')] = b.getAttribute('data-v');
      setChoice(patch);
    });
    if (ideaInput) {
      ideaInput.addEventListener('input', function () {
        clearBtn.hidden = !ideaInput.value;
        setChoice({ idea: ideaInput.value });
      });
      clearBtn.addEventListener('click', function () {
        ideaInput.value = '';
        setChoice({ idea: '' });
        ideaInput.focus();
      });
    }
    if (randomBtn) randomBtn.addEventListener('click', function () {
      function pick(list, cur) {
        var pool = list.filter(function (x) { return x.id !== cur; });
        return pool[Math.floor(Math.random() * pool.length)].id;
      }
      var c = getChoice();
      setChoice({ genre: pick(GENRES, c.genre), hero: pick(HEROES, c.hero), obstacle: pick(OBSTACLES, c.obstacle) });
    });

    var off = subscribe(sync);
    sync();
    return {
      el: wrap,
      getChoice: getChoice,
      setChoice: setChoice,
      prompt: boxCtl,
      destroy: function () { off(); if (boxCtl) boxCtl.destroy(); if (wrap.parentNode) wrap.parentNode.removeChild(wrap); }
    };
  }

  // 프롬프트 상자 하나만 그려요(포스터·음악·영상·합치기).
  function mountPrompt(root, opts) {
    opts = opts || {};
    prepRoot(root);
    var ctl = buildBox(opts);
    root.appendChild(ctl.el);
    return ctl;
  }

  window.GameKit = {
    version: '2026-10-16',
    OPTIONS: {
      genre: GENRES.map(function (g) { return { id: g.id, ko: g.ko }; }),
      hero: HEROES.map(function (h) { return { id: h.id, ko: h.ko, en: h.en }; }),
      obstacle: OBSTACLES.map(function (o) { return { id: o.id, ko: o.ko, en: o.en }; })
    },
    FILES: FILES,
    FOLDER: FOLDER,
    SETS: SETS,
    DEFAULT: Object.assign({}, DEFAULT),
    getChoice: getChoice,
    setChoice: setChoice,
    subscribe: subscribe,
    label: label,
    story: function (choice) { return { ko: strip(storyKo(choice)), en: strip(storyEn(choice)) }; },
    buildPrompt: buildPrompt,
    mediaPrompts: mediaPrompts,
    mergePrompt: mergePrompt,
    text: text,
    suggestSet: suggestSet,
    copyText: copyText,
    mount: mount,
    mountPrompt: mountPrompt,
    josa: function (word, type) { return word + jo(word, type); }
  };
})();
