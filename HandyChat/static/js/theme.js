(function(){
  const KEY = 'fmpe_theme_mode';
  const toggle = () => {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    const next = current === 'light' ? 'dark' : 'light';
    apply(next);
  };
  const apply = (mode) => {
    const html = document.documentElement;
    if(mode === 'light') html.setAttribute('data-theme','light'); else html.removeAttribute('data-theme');
    localStorage.setItem(KEY, mode);
    // update icons on any toggles
    document.querySelectorAll('.theme-toggle .theme-icon').forEach(el=>{
      el.textContent = mode === 'light' ? '☀️' : '🌙';
    });
    document.querySelectorAll('.theme-toggle').forEach(btn=>btn.setAttribute('aria-pressed', mode==='light'));
  };
  // init
  try{
    const saved = localStorage.getItem(KEY);
    if(saved) apply(saved); else apply('dark');
  }catch(e){ /* ignore */ }
  window.toggleTheme = toggle;
})();
