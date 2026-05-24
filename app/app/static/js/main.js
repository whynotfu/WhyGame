// close flash messages on click
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
