'use strict';
const body = document.body;
const scene = document.querySelector('#hero-scene');
const avatarPosition = document.querySelector('#avatar-position');
const avatarButton = document.querySelector('#avatar-button');
const motionButton = document.querySelector('#motion-toggle');
const motionLabel = motionButton.querySelector('.motion-label');
const motionIcon = motionButton.querySelector('.motion-icon');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let motionEnabled = !reducedMotion.matches;
let greetingTimer;
let greetingIndex = 0;
function applyMotion() {
  body.classList.toggle('motion-paused', !motionEnabled);
  motionButton.setAttribute('aria-pressed', String(motionEnabled));
  motionLabel.textContent = motionEnabled ? 'Pause motion' : 'Enable motion';
  motionIcon.textContent = motionEnabled ? 'Ⅱ' : '▷';
  if (!motionEnabled) resetPose();
}
function resetPose() {
  avatarPosition.style.setProperty('--move-x', '0px');
  avatarPosition.style.setProperty('--move-y', '0px');
  avatarPosition.style.setProperty('--turn-y', '0deg');
}
motionButton.addEventListener('click', () => {
  if (reducedMotion.matches) {
    motionEnabled = false;
    showGreeting('Reduced motion is on.');
  } else motionEnabled = !motionEnabled;
  applyMotion();
});
reducedMotion.addEventListener('change', () => { motionEnabled = !reducedMotion.matches; applyMotion(); });
applyMotion();
scene.addEventListener('pointermove', event => {
  if (!motionEnabled || event.pointerType !== 'mouse') return;
  const rect = scene.getBoundingClientRect();
  const x = (event.clientX - rect.left) / rect.width - .5;
  const y = (event.clientY - rect.top) / rect.height - .5;
  avatarPosition.style.setProperty('--move-x', `${x * 17}px`);
  avatarPosition.style.setProperty('--move-y', `${y * 9}px`);
  avatarPosition.style.setProperty('--turn-y', `${x * 12}deg`);
});
scene.addEventListener('pointerleave', resetPose);
const lookButtons = Array.from(document.querySelectorAll('[data-look]'));
function selectLook(look) {
  lookButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.look === look)));
  document.querySelectorAll('.avatar').forEach(avatar => {
    const active = avatar.id === `avatar-${look}`;
    avatar.classList.toggle('avatar-active', active);
    avatar.setAttribute('aria-hidden', String(!active));
  });
  document.querySelector('#floating-note').textContent = look === 'builder' ? 'Ideas into action.' : 'A little more play.';
  document.querySelector('#scene-hint').textContent = look === 'builder' ? 'Build. Learn. Make it better.' : 'Two sides. Same curious mind.';
  resetPose();
}
lookButtons.forEach((button, index) => {
  button.addEventListener('click', () => selectLook(button.dataset.look));
  button.addEventListener('keydown', event => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    event.preventDefault();
    const next = lookButtons[(index + 1) % lookButtons.length];
    next.focus(); selectLook(next.dataset.look);
  });
});
function showGreeting(message) {
  const bubble = document.querySelector('#hello-bubble');
  clearTimeout(greetingTimer);
  bubble.textContent = message;
  bubble.classList.add('is-visible');
  greetingTimer = setTimeout(() => bubble.classList.remove('is-visible'), 2600);
}
avatarButton.addEventListener('click', () => {
  const greetings = ['Hi, I’m Vicky!', 'Stay curious.', 'Good to see you!'];
  showGreeting(greetings[greetingIndex++ % greetings.length]);
  if (motionEnabled) {
    avatarButton.classList.remove('greet');
    void avatarButton.offsetWidth;
    avatarButton.classList.add('greet');
  }
});
avatarButton.addEventListener('animationend', event => { if (event.animationName === 'greet') avatarButton.classList.remove('greet'); });
const dialog = document.querySelector('#artwork-dialog');
document.querySelector('#artwork-button').addEventListener('click', () => dialog.showModal());
document.querySelector('#close-artwork').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
document.querySelector('#year').textContent = new Date().getFullYear();
