(function(){
  var root=document.documentElement;
  function get(k){try{return localStorage.getItem(k)}catch(e){return null}}
  function set(k,v){try{localStorage.setItem(k,v)}catch(e){}}
  function setLang(l,keep){root.dataset.lang=l;root.lang=l;document.querySelectorAll('button[data-lang]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.lang===l))});if(keep)set('lurohome-lang',l)}
  var saved=get('lurohome-lang');
  setLang(saved||((navigator.language||'de').toLowerCase().indexOf('de')===0?'de':'en'));
  document.querySelectorAll('button[data-lang]').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.lang,true)})});
  var t=get('lurohome-theme');if(t==='dark'||t==='light')root.dataset.theme=t;
  document.getElementById('theme').addEventListener('click',function(){
    var dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
    var n=dark?'light':'dark';root.dataset.theme=n;set('lurohome-theme',n)});
})();
