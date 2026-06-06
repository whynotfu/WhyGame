// ── PAGE LOADER ──────────────────────────────────────────────────────
const pageLoader = document.getElementById('pageLoader');
const LOADER_DELAY = 350; // ms — показываем только если переход дольше этого
let loaderTimer = null;

function scheduleLoader() {
  loaderTimer = setTimeout(() => {
    pageLoader.classList.add('is-visible');
  }, LOADER_DELAY);
}

// показываем при переходе по ссылкам (не хеш, не target=_blank, не модалка)
document.addEventListener('click', e => {
  const link = e.target.closest('a[href]');
  if (!link) return;
  const href = link.getAttribute('href');
  if (!href || href.startsWith('#') || href.startsWith('javascript')) return;
  if (link.target === '_blank') return;
  if (e.ctrlKey || e.metaKey || e.shiftKey) return;
  scheduleLoader();
});

// показываем при сабмите форм
document.addEventListener('submit', () => {
  scheduleLoader();
});

// скрываем если браузер вернулся (back/forward кеш)
window.addEventListener('pageshow', e => {
  if (e.persisted) {
    clearTimeout(loaderTimer);
    pageLoader.classList.remove('is-visible');
  }
});

// ── AUTH MODALS ──────────────────────────────────────────────────────
const authOverlay = document.getElementById('authOverlay');

function openModal(name) {
  document.querySelectorAll('.auth-modal').forEach(m => m.classList.remove('is-active'));
  const modal = document.getElementById('modal' + name.charAt(0).toUpperCase() + name.slice(1));
  if (!modal) return;
  modal.classList.add('is-active');
  authOverlay.classList.add('is-open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  authOverlay.classList.remove('is-open');
  document.body.style.overflow = '';
  setTimeout(() => {
    document.querySelectorAll('.auth-modal').forEach(m => m.classList.remove('is-active'));
  }, 220);
}

function handleOverlayClick(e) {
  if (e.target === authOverlay || e.target === authOverlay.querySelector('.auth-overlay__backdrop')) {
    closeModal();
  }
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// ── AVATAR DROPDOWNS ──────────────────────────────────────────────────
// JS hover so mouse can travel avatar→dropdown without closing
document.querySelectorAll('.profile-avatar--loggedin, .profile-avatar--guest').forEach(avatar => {
  const dropdown = avatar.querySelector('.avatar-dropdown');
  if (!dropdown) return;

  let closeTimer = null;

  function openDropdown() {
    clearTimeout(closeTimer);
    dropdown.classList.add('is-open');
  }
  function scheduleClose() {
    closeTimer = setTimeout(() => dropdown.classList.remove('is-open'), 120);
  }

  avatar.addEventListener('mouseenter', openDropdown);
  avatar.addEventListener('mouseleave', scheduleClose);
  dropdown.addEventListener('mouseenter', openDropdown);
  dropdown.addEventListener('mouseleave', scheduleClose);
});

// ── FLASH ─────────────────────────────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  el.style.cursor = 'pointer';
  el.addEventListener('click', () => el.remove());
});

// search.gif — static on load, animates on hover
const gif = document.getElementById('searchGif');
if (gif) {
  const gifSrc = gif.dataset.src;
  let staticFrame = null;

  // capture first frame once the gif loads
  const capture = () => {
    const canvas = document.createElement('canvas');
    canvas.width  = gif.naturalWidth  || 44;
    canvas.height = gif.naturalHeight || 44;
    canvas.getContext('2d').drawImage(gif, 0, 0);
    staticFrame = canvas.toDataURL('image/png');
    gif.src = staticFrame; // freeze
  };

  if (gif.complete && gif.naturalWidth) {
    capture();
  } else {
    gif.addEventListener('load', capture, { once: true });
  }

  gif.addEventListener('mouseenter', () => {
    // restart gif from frame 1 so animation plays
    gif.src = gifSrc + '?t=' + Date.now();
  });

  gif.addEventListener('mouseleave', () => {
    if (staticFrame) gif.src = staticFrame;
  });
}
