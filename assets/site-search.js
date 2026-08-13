(() => {
  const ASSET_VERSION='20260730-cpsgt-live1';
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
  addStylesheet('/assets/blog-badge-brand.css');
  addStylesheet('/assets/home-mission.css');

  const $=(s,c=document)=>c.querySelector(s);
  const $$=(s,c=document)=>[...c.querySelectorAll(s)];
  const esc=s=>String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const trademarkPattern=/™|&trade;|&#8482;|&#x2122;/gi;

  function removeTrademarkSymbols(root=document){
    const scope=root.nodeType===9?root:root.ownerDocument||document;
    if(scope.title)scope.title=scope.title.replace(trademarkPattern,'');
    const walker=scope.createTreeWalker(root.nodeType===9?root.documentElement:root,NodeFilter.SHOW_TEXT);
    let node;
    while((node=walker.nextNode())){
      const parent=node.parentElement;
      if(parent&&/^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA)$/i.test(parent.tagName))continue;
      if(trademarkPattern.test(node.nodeValue||''))node.nodeValue=(node.nodeValue||'').replace(trademarkPattern,'');
      trademarkPattern.lastIndex=0;
    }
    const base=root.nodeType===9?root:root;
    if(base.querySelectorAll){
      base.querySelectorAll('[title],[aria-label],[alt],meta[content]').forEach(el=>{
        ['title','aria-label','alt','content'].forEach(name=>{
          if(!el.hasAttribute(name))return;
          const value=el.getAttribute(name)||'';
          if(trademarkPattern.test(value))el.setAttribute(name,value.replace(trademarkPattern,''));
          trademarkPattern.lastIndex=0;
        });
      });
    }
  }

  const brand=$('.brand');
  if(brand && !$('.spg-brand-badge',brand)){
    const title=$('strong',brand);
    const subtitle=$(':scope > span',brand);
    const copy=document.createElement('div');
    copy.className='spg-brand-copy';
    if(title){title.textContent='Sleep Pathways Guild Blog';copy.appendChild(title)}
    if(subtitle)copy.appendChild(subtitle);
    const badge=document.createElement('img');
    badge.className='spg-brand-badge';
    badge.src='/assets/blogger/badge-9316.png';
    badge.alt='Sleep Pathways Guild badge logo';
    badge.width=60;
    badge.height=60;
    brand.classList.add('spg-brand-enhanced');
    brand.prepend(badge);
    brand.appendChild(copy);
    brand.setAttribute('aria-label','Sleep Pathways Guild Blog home');
  }

  const overlay=document.createElement('div');
  overlay.className='search-overlay';
  overlay.innerHTML=`<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search Sleep Pathways Guild Blog"><div class="search-head"><div><strong>Search the blog</strong><span>Find articles, lessons, scoring topics, and study resources</span></div><button class="search-close" aria-label="Close search">×</button></div><input class="search-input" type="search" placeholder="Try: CPSGT, respiratory events, EKG, pediatric, RPSGT…" autocomplete="off"><div class="search-chips"><button data-q="CPSGT">CPSGT Exam Prep</button><button data-q="RPSGT">RPSGT Exam Prep</button><button data-q="scoring">Scoring</button><button data-q="pediatric">Pediatric</button><button data-q="EKG">EKG</button><button data-q="respiratory">Respiratory</button></div><div class="search-status">Start typing to search all articles.</div><div class="search-results"></div></div>`;
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

  if(path==='/' && !$('.spg-home-mission')){
    const section=document.createElement('section');
    section.className='spg-home-mission';
    section.setAttribute('aria-labelledby','spg-home-mission-title');
    section.innerHTML=`<span class="spg-home-kicker">Free public learning • Education first</span><h2 id="spg-home-mission-title">A guild for the craft of sleep technology.</h2><p>Sleep Pathways Guild is an independent, peer-led educational project founded by <strong>Tracy Frazier, RHIT, RPSGT, CCS-P</strong>. The blog is one part of a wider collection of free public webapps, labs, articles, downloads, and professional support for RPSGT learners, CPSGT learners, students, and working technologists.</p><div class="spg-home-mission-grid"><article class="spg-home-mission-card"><h3>Founded by Tracy Frazier, RHIT, RPSGT, CCS-P</h3><p>Tracy created the Guild from her experience as a sleep technologist, health information professional, credentialed coding specialist, learner, and educator. She believes serious learners deserve practical explanations, free public tools, encouragement, and a place to begin without cost being the first obstacle.</p></article><article class="spg-home-mission-card"><h3>Inspired by mentor Robert Dopson, RPSGT</h3><p>Robert never turned away an intern or serious learner. He taught in a Socratic way, asking <strong>who, what, when, where, why, and to what extent</strong> before answering the question. That habit of careful inquiry remains part of the Guild’s educational foundation.</p></article><article class="spg-home-mission-card"><h3>Honoring William C. Dement, MD, PhD</h3><p>The Guild honors the memory of Dr. Dement, a founder of sleep medicine, legendary teacher, and public advocate. His verified motto was: <strong>“Drowsiness is red alert.”</strong> <a href="https://med.stanford.edu/news/all-news/2020/06/william-dement-giant-in-field-of-sleep-medicine-dies-at-91.html" target="_blank" rel="noopener">Read Stanford Medicine’s remembrance.</a></p></article><article class="spg-home-mission-card"><h3>Free public offerings</h3><p>Open the released <a href="https://sleeppathwaysguild.com/cpsgt-study-app.html">CPSGT Study Launchpad</a>, the RPSGT study webapp, EKG Skills Lab, free study downloads, and blog lessons. Buying a book is never required to begin learning.</p></article></div><div class="spg-home-mission-actions"><a class="primary" href="https://sleeppathwaysguild.com/#free-resources">Explore Free Guild Resources</a><a class="secondary" href="https://sleeppathwaysguild.com/cpsgt-study-app.html">Launch the CPSGT Webapp</a><a class="secondary" href="https://sleeppathwaysguild.com/RPSGTv2.2026.html">Launch the RPSGT Webapp</a><a class="secondary" href="/downloads/">Open Free Downloads</a></div>`;
    const hero=$('.hero');
    if(hero)hero.insertAdjacentElement('afterend',section);
    else $('main')?.prepend(section);

    if(!$('.spg-release-announcement')){
      const announcement=document.createElement('aside');
      announcement.className='spg-release-announcement';
      announcement.setAttribute('aria-labelledby','spg-cpsgt-release-title');
      announcement.innerHTML=`<span class="spg-release-kicker">Now released</span><h2 id="spg-cpsgt-release-title">The free CPSGT Study Launchpad is live.</h2><p>Start with 600 original practice questions, a 75-question mock-style exam, flashcards, Math Coach, equipment review, missed-question repair, and personalized progress reports. No purchase or account is required.</p><div class="spg-release-actions"><a class="primary" href="https://sleeppathwaysguild.com/cpsgt-study-app.html">Launch the Free CPSGT Webapp</a><a class="secondary" href="/2026/07/free-cpsgt-study-app-released.html">Read the release announcement</a></div>`;
      section.insertAdjacentElement('afterend',announcement);
    }
  }

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

  const lightComponentSelector=[
    '.spg-badge','.spg-task','.spg-tag','.resource-label','.search-category',
    '.spg-card','.spg-mini','.spg-warning','.spg-green','.spg-question',
    '.spg-answer','.spg-checklist label','.spg-footer','.spg-notice',
    '.official-resource-card'
  ].join(',');
  const readableTextSelector='h1,h2,h3,h4,h5,h6,p,li,span,strong,b,em,i,small,label,summary,figcaption';

  function detectDarkSurfaces(){
    $$('.post-content div,.post-content section,.post-content aside,.post-content article').forEach(el=>{
      el.classList.remove('spg-dark-surface');
      const colors=colorsFrom(getComputedStyle(el));
      if(!colors.length)return;
      const avg=colors.reduce((sum,c)=>sum+luminance(c),0)/colors.length;
      if(avg<.18)el.classList.add('spg-dark-surface');
    });
  }

  function applyDarkContrast(){
    $$('.post-content .spg-dark-surface').forEach(surface=>{
      surface.style.setProperty('color','#ffffff','important');
      surface.style.setProperty('-webkit-text-fill-color','#ffffff','important');
      surface.querySelectorAll(readableTextSelector).forEach(node=>{
        const lightParent=node.closest(lightComponentSelector);
        if(lightParent && surface.contains(lightParent))return;
        if(node.closest('.spg-btn,.spg-button,.spg-button-blue,.read,.nav-action,button,[role="button"]'))return;
        node.style.setProperty('color','#ffffff','important');
        node.style.setProperty('-webkit-text-fill-color','#ffffff','important');
        node.style.setProperty('opacity','1','important');
        node.style.setProperty('text-shadow','none','important');
      });
    });
  }

  function applyLightContrast(){
    $$('.post-content '+lightComponentSelector.split(',').join(',.post-content ')).forEach(el=>{
      const colors=colorsFrom(getComputedStyle(el));
      if(!colors.length)return;
      const avg=colors.reduce((sum,c)=>sum+luminance(c),0)/colors.length;
      if(avg<.5)return;
      el.style.setProperty('color','#17324c','important');
      el.style.setProperty('-webkit-text-fill-color','#17324c','important');
      el.style.setProperty('opacity','1','important');
      el.style.setProperty('text-shadow','none','important');
      el.querySelectorAll(readableTextSelector).forEach(node=>{
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
  }

  function applyRevealGold(){
    const selector='.post-content details>summary,.post-content details.spg-reveal>summary,.post-content details[class*="reveal"]>summary';
    $$(selector).forEach(summary=>{
      summary.style.setProperty('background','#071a2e','important');
      summary.style.setProperty('color','#f6d365','important');
      summary.style.setProperty('-webkit-text-fill-color','#f6d365','important');
      summary.style.setProperty('border','2px solid #d5a62e','important');
      summary.style.setProperty('border-radius','12px','important');
      summary.style.setProperty('padding','14px 18px','important');
      summary.style.setProperty('opacity','1','important');
      summary.style.setProperty('font-weight','800','important');
      summary.style.setProperty('line-height','1.35','important');
      summary.style.setProperty('text-shadow','none','important');
      summary.style.setProperty('cursor','pointer','important');
      summary.querySelectorAll('*').forEach(node=>{
        node.style.setProperty('color','#f6d365','important');
        node.style.setProperty('-webkit-text-fill-color','#f6d365','important');
        node.style.setProperty('opacity','1','important');
        node.style.setProperty('text-shadow','none','important');
      });
    });
  }

  function refreshContrast(){detectDarkSurfaces();applyDarkContrast();applyLightContrast();applyRevealGold()}
  refreshContrast();
  requestAnimationFrame(refreshContrast);
  setTimeout(refreshContrast,250);
  setTimeout(refreshContrast,1000);
  const postContent=$('.post-content');
  if(postContent){new MutationObserver(refreshContrast).observe(postContent,{childList:true,subtree:true})}
  document.addEventListener('toggle',e=>{if(e.target.matches&&e.target.matches('.post-content details'))applyRevealGold()},true);

  removeTrademarkSymbols(document);
  let cleanupQueued=false;
  new MutationObserver(()=>{
    if(cleanupQueued)return;
    cleanupQueued=true;
    requestAnimationFrame(()=>{cleanupQueued=false;removeTrademarkSymbols(document)});
  }).observe(document.documentElement,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['title','aria-label','alt','content']});

  document.documentElement.dataset.spgContrast='reveal-gold-1';
  document.documentElement.dataset.spgBranding='copyright-only';
  document.documentElement.dataset.spgHomepage='cpsgt-released-1';
})();