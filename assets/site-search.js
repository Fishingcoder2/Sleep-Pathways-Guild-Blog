(() => {
  const modernStyle=document.createElement('link');
  modernStyle.rel='stylesheet';
  modernStyle.href='/assets/search-modern.css';
  document.head.appendChild(modernStyle);
  const brandStyle=document.createElement('link');
  brandStyle.rel='stylesheet';
  brandStyle.href='/assets/brand-teal-blue.css';
  document.head.appendChild(brandStyle);
  const $=(s,c=document)=>c.querySelector(s);
  const $$=(s,c=document)=>[...c.querySelectorAll(s)];
  const esc=s=>String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const overlay=document.createElement('div');
  overlay.className='search-overlay';
  overlay.innerHTML=`<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search Sleep Pathways Guild Blog"><div class="search-head"><div><strong>Search the blog</strong><span>Find articles, lessons, scoring topics, and study resources</span></div><button class="search-close" aria-label="Close search">×</button></div><input class="search-input" type="search" placeholder="Try: respiratory events, EKG, pediatric, RPSGT…" autocomplete="off"><div class="search-chips"><button data-q="RPSGT">RPSGT Exam Prep</button><button data-q="scoring">Scoring</button><button data-q="pediatric">Pediatric</button><button data-q="EKG">EKG</button><button data-q="respiratory">Respiratory</button></div><div class="search-status">Start typing to search all articles.</div><div class="search-results"></div></div>`;
  document.body.appendChild(overlay);
  let index=[];
  fetch('/assets/search-index.json').then(r=>r.json()).then(d=>index=d).catch(()=>{});
  const input=$('.search-input',overlay), results=$('.search-results',overlay), status=$('.search-status',overlay);
  function openSearch(q=''){overlay.classList.add('open');document.body.classList.add('search-open');setTimeout(()=>input.focus(),40);if(q){input.value=q;run(q)}}
  function closeSearch(){overlay.classList.remove('open');document.body.classList.remove('search-open')}
  function run(q){q=q.trim().toLowerCase();results.innerHTML='';if(!q){status.textContent='Start typing to search all articles.';return}const terms=q.split(/\s+/);const found=index.map(x=>{const hay=(x.title+' '+x.description+' '+x.category).toLowerCase();let score=0;terms.forEach(t=>{if(x.title.toLowerCase().includes(t))score+=5;if(x.category.toLowerCase().includes(t))score+=3;if(hay.includes(t))score+=1});return {...x,score}}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,20);status.textContent=found.length?`${found.length} result${found.length===1?'':'s'} found`:'No results found. Try a broader term.';results.innerHTML=found.map(x=>`<a class="search-result" href="${esc(x.url)}"><span class="search-category">${esc(x.category)}</span><strong>${esc(x.title)}</strong><p>${esc(x.description||'Open this article')}</p></a>`).join('')}
  input.addEventListener('input',e=>run(e.target.value));
  $$('.search-chips button',overlay).forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.q;run(b.dataset.q);input.focus()}));
  $('.search-close',overlay).addEventListener('click',closeSearch);overlay.addEventListener('click',e=>{if(e.target===overlay)closeSearch()});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeSearch();if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}});
  $$('.js-search').forEach(b=>b.addEventListener('click',()=>openSearch()));
  const menuBtn=$('.menu-toggle'), nav=$('.site-nav'); if(menuBtn&&nav)menuBtn.addEventListener('click',()=>{const on=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(on))});
  const path=location.pathname; $$('.site-nav a').forEach(a=>{const href=a.getAttribute('href'); if(href==='/'?path==='/':href&&path.startsWith(href))a.classList.add('active')});
})();