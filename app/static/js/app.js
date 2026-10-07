/* Progressive enhancements only. Every form submits to Flask. */
(() => {
  const toggle = document.getElementById('nav-toggle');
  const closeNavigation = () => {
    document.body.classList.remove('sidebar-open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  };
  if (toggle) toggle.addEventListener('click', () => {
    const opened = document.body.classList.toggle('sidebar-open');
    toggle.setAttribute('aria-expanded', String(opened));
  });
  document.getElementById('nav-scrim')?.addEventListener('click', closeNavigation);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeNavigation();
  });
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });
  const allFunds = document.getElementById('select-all-funds');
  if (allFunds) allFunds.addEventListener('click', () => {
    const boxes = Array.from(document.querySelectorAll('input[name="fund_ids"]'));
    const checked = !boxes.every(box => box.checked);
    boxes.forEach(box => { box.checked = checked; });
    allFunds.textContent = checked ? 'Снять все отметки' : 'Выбрать все';
  });
  const copy = document.getElementById('copy-token');
  if (copy) copy.addEventListener('click', async () => {
    const token = document.getElementById('generated-token');
    const status = document.getElementById('copy-status');
    try {
      await navigator.clipboard.writeText(token.value);
      status.textContent = 'Токен скопирован';
    } catch (_) {
      token.focus();
      token.select();
      status.textContent = 'Нажмите Ctrl+C, чтобы скопировать';
    }
  });
})();
