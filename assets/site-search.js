(() => {
  const ASSET_VERSION='20260723-contrast4';
  function addStylesheet(path){
    const link=document.createElement('link');
    link.rel='stylesheet';
    link.href=`${path}?v=${ASSET_VERSION}`;
    document.head.appendChild(link);
  }
  addStylesheet('/assets/search-modern.css');
  addStylesheet('/assets/brand-teal-blue.css');
  addStylesheet('/assets/resource-enhancements.css');
  addStylesheet('/assets/guild-gold-accent.css');

  const $=(s,c=document)=>c.querySelector(s);
  const $$=(s,c=document)=>[...c.querySelectorAll(s)];
  const esc=s=>String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

  const overlay=document.createElement('div');
  overlay.className='search-overlay';
  overlay.innerHTML=`<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search Sleep Pathways Guild Blog"><div class="search-head"><div><strong>Search the blog</strong><span>Find articles, lessons, scoring topics, and study resources</span></div><button class="search-close" aria-label="Close search">×</button></div><input class="search-input" type="search" placeholder="Try: respiratory events, EKG, pediatric, RPSGT…" autocomplete="off"><div class="search-chips"><button data-q="RPSGT">RPSGT Exam Prep</button><button data-q="scoring">Scoring</button><button data-q="pediatric">Pediatric</button><button data-q="EKG">EKG</button><button data-q="respiratory">Respiratory</button></div><div class="search-status">Start typing to search all articles.</div><div class="search-results"></div></div>`;
  document.body.appendChild(overlay);

  let index=[];
  fetch(`/assets/search-index.json?v=${ASSET_VERSION}`).then(r=>r.json()).then(d=>index=d).catch(()=>{});
  const input=$('.search-input',overlay), results=$('.search-results',overlay), status=$('.search-status',overlay);
  function openSearch(q=''){overlay.classList.add('open');document.body.classList.add('search-open');setTimeout(()=>input.focus(),40);if(q){input.value=q;run(q)}}
  function closeSearch(){overlay.classList.remove('open');document.body.classList.remove('search-open')}
  function run(q){q=q.trim().toLowerCase();results.innerHTML='';if(!q){status.textContent='Start typing to search all articles.';return}const terms=q.split(/\s+/);const found=index.map(x=>{const hay=(x.title+' '+x.description+' '+x.category).toLowerCase();let score=0;terms.forEach(t=>{if(x.title.toLowerCase().includes(t))score+=5;if(x.category.toLowerCase().includes(t))score+=3;if(hay.includes(t))score+=1});return {...x,score}}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,20);status.textContent=found.length?`${found.length} result${found.length===1?'':'s'} found`:'No results found. Try a broader term.';results.innerHTML=found.map(x=>`<a class="search-result" href="${esc(x.url)}"><span class="search-category">${esc(x.category)}</span><strong>${esc(x.title)}</strong><p>${esc(x.description||'Open this article')}</p></a>`).join('')}
  input.addEventListener('input',e=>run(e.target.value));
  $$('.search-chips button',overlay).forEach(b=>b.addEventListener('click',()=>{input.value=b.dataset.q;run(b.dataset.q);input.focus()}));
  $('.search-close',overlay).addEventListener('click',closeSearch);
  overlay.addEventListener('click',e=>{if(e.target===overlay)closeSearch()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeSearch();if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}});
  $$('.js-search').forEach(b=>b.addEventListener('click',()=>openSearch()));
  const menuBtn=$('.menu-toggle'), nav=$('.site-nav');
  if(menuBtn&&nav)menuBtn.addEventListener('click',()=>{const on=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(on))});
  const path=location.pathname;
  $$('.site-nav a').forEach(a=>{const href=a.getAttribute('href');if(href==='/'?path==='/':href&&path.startsWith(href))a.classList.add('active')});

  if(path==='/p/rpsgt-exam-prep-book-store.html'){
    const studyTools=$('#study-tools');
    if(studyTools && !$('#official-study-resources')){
      const section=document.createElement('section');
      section.id='official-study-resources';
      section.className='official-study-resources';
      section.innerHTML=`<h2>Official Study Resources</h2><p class="resource-intro">Use these official professional and credentialing resources to verify current clinical guidance, technical procedures, exam eligibility, and exam content.</p><div class="official-resource-grid"><article class="official-resource-card"><span class="resource-label">AASM</span><h3>AASM Practice Guidelines</h3><p>Current clinical practice guidelines and guidance statements for the diagnosis, treatment, and long-term management of sleep disorders.</p><a href="https://aasm.org/clinical-resources/practice-standards/practice-guidelines/" target="_blank" rel="noopener">Open AASM Guidelines</a></article><article class="official-resource-card"><span class="resource-label">AAST</span><h3>AAST Technical Guidelines</h3><p>Professional technical guidance for sleep technologists, including standard polysomnography, PAP titration, HSAT, CO₂ monitoring, and related procedures.</p><a href="https://aastweb.org/clinical-resources/technical-guidelines/" target="_blank" rel="noopener">Open AAST Guidelines</a></article><article class="official-resource-card"><span class="resource-label">BRPT</span><h3>RPSGT Candidate Handbook</h3><p>Official eligibility pathways, application procedures, examination policies, scoring information, and candidate requirements.</p><a href="https://brpt.org/rpsgt/rpsgt-handbook-2/" target="_blank" rel="noopener">Open RPSGT Handbook</a></article><article class="official-resource-card"><span class="resource-label">BRPT</span><h3>RPSGT Exam Blueprint</h3><p>The official domains, tasks, knowledge areas, and exam structure used for the current RPSGT examination.</p><a href="https://brpt.org/rpsgt/exam-blueprint/" target="_blank" rel="noopener">Open Exam Blueprint</a></article></div>`;
      studyTools.parentNode.insertBefore(section,studyTools);
      const heroActions=$('.spg-hero-actions');
      if(heroActions){const link=document.createElement('a');link.className='spg-btn secondary';link.href='#official-study-resources';link.textContent='Official Study Resources';heroActions.appendChild(link)}
    }
  }

  function luminance(rgb){const [r,g,b]=rgb.map(v=>v/255).map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));return .2126*r+.7152*g+.0722*b}
  function colorsFrom(style){
    const text=`${style.backgroundColor} ${style.backgroundImage}`;
    const rgb=[...text.matchAll(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/gi)]
      .filter(m=>m[4]===undefined || Number(m[4])>=.35)
      .map(m=>[+m[1],+m[2],+m[3]]);
    const hex=[...text.matchAll(/#([0-9a-f]{6}|[0-9a-f]{3})(?![0-9a-f])/gi)].map(m=>{
      let h=m[1];if(h.length===3)h=h.split('').map(c=>c+c).join('');
      return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)];
    });
    return rgb.concat(hex);
  }

  function detectDarkSurfaces(){
    $$('.post-content div,.post-content section,.post-content aside,.post-content article').forEach(el=>{
      el.classList.remove('spg-dark-surface');
      const colors=colorsFrom(getComputedStyle(el));
      if(!colors.length)return;
      const avg=colors.reduce((sum,c)=>sum+luminance(c),0)/colors.length;
      if(avg<.18)el.classList.add('spg-dark-surface');
    });
  }

  function applyFinalContrast(){
    const lightSelector=[
      '.post-content .spg-badge',
      '.post-content .spg-task',
      '.post-content .spg-tag',
      '.post-content .resource-label',
      '.post-content .spg-card',
      '.post-content .spg-mini',
      '.post-content .spg-warning',
      '.post-content .spg-green',
      '.post-content .spg-question',
      '.post-content .spg-answer',
      '.post-content details',
      '.post-content .spg-checklist label',
      '.post-content .spg-footer',
      '.post-content .spg-notice',
      '.post-content .official-resource-card'
    ].join(',');
    $$(lightSelector).forEach(el=>{
      const colors=colorsFrom(getComputedStyle(el));
      if(!colors.length)return;
      const avg=colors.reduce((sum,c)=>sum+luminance(c),0)/colors.length;
      if(avg<.5)return;
      el.style.setProperty('color','#17324c','important');
      el.style.setProperty('-webkit-text-fill-color','#17324c','important');
      el.style.setProperty('opacity','1','important');
      el.style.setProperty('text-shadow','none','important');
      el.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,span,strong,b,em,i,small,label,summary,figcaption').forEach(node=>{
        if(node.closest('.spg-btn,.spg-button,.spg-button-blue,.read,.nav-action,button,[role="button"]'))return;
        node.style.setProperty('color','#17324c','important');
        node.style.setProperty('-webkit-text-fill-color','#17324c','important');
        node.style.setProperty('opacity','1','important');
        node.style.setProperty('text-shadow','none','important');
      });
      el.querySelectorAll('a:not(.spg-btn):not(.spg-button):not(.spg-button-blue):not(.read)').forEach(link=>{
        link.style.setProperty('color','#075f91','important');
        link.style.setProperty('-webkit-text-fill-color','#075f91','important');
      });
    });
    document.documentElement.dataset.spgContrast='contrast4';
  }

  function refreshContrast(){detectDarkSurfaces();applyFinalContrast()}
  refreshContrast();
  requestAnimationFrame(refreshContrast);
  setTimeout(refreshContrast,250);
  setTimeout(refreshContrast,1000);
  const postContent=$('.post-content');
  if(postContent){
    new MutationObserver(refreshContrast).observe(postContent,{childList:true,subtree:true});
  }
})();