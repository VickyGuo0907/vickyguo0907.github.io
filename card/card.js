'use strict';

const cardUrl = document.body.dataset.cardUrl;
const cardName = document.body.dataset.cardName;
const shareButton = document.querySelector('#share-card');
const status = document.querySelector('#share-status');
const fallback = document.querySelector('#copy-fallback');
const linkInput = document.querySelector('#card-link');
const dialog = document.querySelector('#qr-dialog');
const qrLink = document.querySelector('#show-qr');
const qrStatus = document.querySelector('#qr-status');

async function copyLink() {
  try {
    if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
    await navigator.clipboard.writeText(cardUrl);
    status.textContent = 'Contact-page link copied.';
    qrStatus.textContent = 'Link copied.';
    fallback.hidden = true;
  } catch {
    if (dialog.open) dialog.close();
    fallback.hidden = false;
    linkInput.focus();
    linkInput.select();
    status.textContent = 'Select and copy the link below.';
  }
}

shareButton.hidden = false;
shareButton.addEventListener('click', async () => {
  status.textContent = '';
  if (navigator.share) {
    try {
      await navigator.share({ title: `${cardName} — Let’s connect`, url: cardUrl });
      return;
    } catch (error) {
      if (error.name === 'AbortError') return;
    }
  }
  await copyLink();
});

if (typeof dialog.showModal === 'function') {
  qrLink.addEventListener('click', event => {
    event.preventDefault();
    qrStatus.textContent = '';
    dialog.showModal();
  });
  document.querySelector('#close-qr').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
}
document.querySelector('#copy-link').addEventListener('click', copyLink);
