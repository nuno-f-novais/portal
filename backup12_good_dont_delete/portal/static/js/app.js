
(function(){
  function apply(theme){
    document.documentElement.setAttribute('data-theme', theme);
  }
  function current(){
    return document.documentElement.getAttribute('data-theme') || 'light';
  }
  function init(){
    var stored = localStorage.getItem('portal-theme');
    if(!stored){
      // infer from system once
      var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      stored = prefersDark ? 'dark' : 'light';
      localStorage.setItem('portal-theme', stored);
    }
    apply(stored);
    var btn = document.getElementById('themeToggle');
    if(btn){
      btn.addEventListener('click', function(){
        var next = current()==='dark' ? 'light' : 'dark';
        localStorage.setItem('portal-theme', next);
        apply(next);
      });
    }
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
