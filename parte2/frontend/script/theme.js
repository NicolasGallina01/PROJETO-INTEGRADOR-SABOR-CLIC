/* Modo alto contraste consistente e persistente entre páginas. */
(() => {
  const KEY = 'saborclic_contraste';
  const isActive = () => document.documentElement.dataset.theme === 'contrast';
  function apply(active) {
    document.documentElement.dataset.theme = active ? 'contrast' : 'default';
    try { localStorage.setItem(KEY, active ? 'sim' : 'nao'); } catch (_) { /* armazenamento bloqueado */ }
    document.querySelectorAll('[data-action="contrast"]').forEach(button => {
      button.setAttribute('aria-pressed', String(active));
      button.title = active ? 'Desativar alto contraste' : 'Ativar alto contraste';
    });
    const state = document.getElementById('contrast-state');
    if (state) state.textContent = active ? 'Ativado' : 'Desativado';
  }
  let active = false;
  try { active = (localStorage.getItem(KEY) || localStorage.getItem('altocontraste_saborclic')) === 'sim'; } catch (_) { /* modo padrão */ }
  document.documentElement.dataset.theme = active ? 'contrast' : 'default';
  document.addEventListener('DOMContentLoaded', () => apply(active));
  document.addEventListener('click', event => {
    if (event.target.closest('[data-action="contrast"]')) apply(!isActive());
  });
})();
