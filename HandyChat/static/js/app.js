// Simple demo app - stores data in localStorage and supports natural query keywords (basic)
(function(){
  // demo data seed (only if localStorage empty)
  const seed = [
    {id:'gym-a', name:'Gym A', details:'Building B, 2nd floor', sport:'basketball', photos:[], teacher:'Coach Wang', contact:'wang@uni.edu', freq:'semester'},
    {id:'pool', name:'Swimming Pool', details:'Sports center, ground floor', sport:'swimming', photos:[], teacher:'Coach Li', contact:'li@uni.edu', freq:'semester'},
    {id:'gym-b', name:'Gym B', details:'Main hall, 1st floor', sport:'badminton', photos:[], teacher:'Coach Zhao', contact:'zhao@uni.edu', freq:'weekly'},
    {id:'court', name:'Outdoor Courts', details:'North campus courts', sport:'tabletennis', photos:[], teacher:'Coach A', contact:'a@uni.edu', freq:'semester'}
  ];

  function loadLocations(){
    const raw = localStorage.getItem('fmpe_locations');
    if(!raw){ localStorage.setItem('fmpe_locations', JSON.stringify(seed)); return seed; }
    try{ return JSON.parse(raw) }catch(e){ localStorage.setItem('fmpe_locations', JSON.stringify(seed)); return seed }
  }
  function saveLocations(list){ localStorage.setItem('fmpe_locations', JSON.stringify(list)); }

  let locations = loadLocations();

  // UI refs
  const results = document.getElementById('results');
  const askBtn = document.getElementById('askBtn');
  const query = document.getElementById('query');
  const photosEl = document.getElementById('photos');
  const infoPanel = document.getElementById('infoPanel');
  const locName = document.getElementById('locName');
  const locDetails = document.getElementById('locDetails');
  const meta = document.getElementById('meta');
  const campus = document.getElementById('campus');

  // render list in left panel (if present)
  function renderList(filter){
    if(!results) return;
    results.innerHTML = '';
    const list = locations.filter(l => !filter || l.sport.toLowerCase().includes(filter.toLowerCase()));
    list.forEach(l => {
      const r = document.createElement('div'); r.className = 'result';
      r.innerHTML = `<div class="icon">${emojiFor(l.sport)}</div><div class="details"><h4>${escapeHtml(l.name)}</h4><p>${escapeHtml(l.sport)} · ${escapeHtml(l.details)}</p></div>`;
      r.onclick = ()=> showLocation(l.id);
      results.appendChild(r);
    });
  }

  // map interactivity - clicking buildings
  document.querySelectorAll('.building').forEach(g => g.addEventListener('click', ()=>{
    const id = g.getAttribute('data-id');
    showLocation(id);
  }));

  function showLocation(id){
    const loc = locations.find(x=>x.id===id);
    if(!loc) return notFound();
    locName.textContent = loc.name;
    locDetails.textContent = `${loc.details} · ${loc.freq} change`;
    meta.innerHTML = `<div class="tag">Teacher: ${escapeHtml(loc.teacher||'—')}</div><div class="tag" style="margin-left:8px">Contact: ${escapeHtml(loc.contact||'—')}</div>`;

    photosEl.innerHTML = '';
    (loc.photos || []).slice(0,4).forEach(url=>{
      const im = document.createElement('img'); im.src = url; photosEl.appendChild(im);
    });

    // highlight building visually by flicker
    document.querySelectorAll('.bld').forEach(b=>b.style.opacity=0.6);
    const g = document.querySelector(`.building[data-id="${id}"] .bld`);
    if(g){ g.style.opacity=1; g.style.transform='translateY(-6px) scale(1.02)'; setTimeout(()=>g.style.transform='translateY(-6px)',600); }

    // save last viewed for student quick access
    localStorage.setItem('fmpe_last_view', id);
  }

  function notFound(){
    locName.textContent = 'Not found';
    locDetails.textContent = 'No matching location for that query.';
    meta.innerHTML = '';
    photosEl.innerHTML = '';
  }

  // basic natural language-ish query parsing (keyword match)
  function handleQuery(q){
    if(!q) return renderList();
    q = q.trim().toLowerCase();
    // if question contains sport names or Chinese equivalents, map them
    const map = {'basketball':'basketball','🏀':'basketball','羽毛球':'badminton','badminton':'badminton','ping':'tabletennis','table':'tabletennis','乒乓':'tabletennis','ping pong':'tabletennis','swim':'swimming','游泳':'swimming'};
    for(const k in map){
      if(q.includes(k)) return showBySport(map[k]);
    }
    // try to match by teacher name
    const teacherMatch = locations.find(l => (l.teacher||'').toLowerCase().includes(q));
    if(teacherMatch) return showLocation(teacherMatch.id);
    // try id or name
    const idMatch = locations.find(l => l.id.toLowerCase()===q || l.name.toLowerCase()===q);
    if(idMatch) return showLocation(idMatch.id);
    notFound();
  }

  function showBySport(sport){
    const loc = locations.find(l=>l.sport&&l.sport.toLowerCase().includes(sport.toLowerCase()));
    if(loc) return showLocation(loc.id);
    notFound();
  }

  // helpers
  function emojiFor(s){ if(!s) return '🏳️'; s=s.toLowerCase(); if(s.includes('basket')) return '🏀'; if(s.includes('badminton')) return '🏸'; if(s.includes('swim')) return '🏊'; if(s.includes('table')) return '🏓'; return '⚽' }
  function escapeHtml(t){ return (t||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }

  // attach search handlers if available
  if(askBtn){
    askBtn.addEventListener('click', ()=> handleQuery(query.value));
    query.addEventListener('keydown', (e)=>{ if(e.key==='Enter') handleQuery(query.value) });
    document.querySelectorAll('.chip').forEach(b=>b.addEventListener('click', ()=>{ renderList(b.getAttribute('data-filter')) }));
  }

  renderList();

  // Teacher page handlers: save locations
  const saveBtn = document.getElementById('saveLoc');
  if(saveBtn){
    saveBtn.addEventListener('click', (ev)=>{
      ev.preventDefault();
      const id = document.getElementById('locId').value.trim();
      if(!id){ alert('Please set a unique id'); return; }
      const obj = {
        id,
        name: document.getElementById('locName').value.trim()||id,
        details: document.getElementById('locFloor').value.trim(),
        sport: document.getElementById('locSport').value.trim(),
        photos: document.getElementById('photoUrl').value? [document.getElementById('photoUrl').value.trim()] : [],
        teacher: document.getElementById('teacherName').value.trim(),
        contact: document.getElementById('teacherContact').value.trim(),
        freq: document.getElementById('changeFreq').value
      };
      const found = locations.find(l=>l.id===id);
      if(found){
        Object.assign(found, obj);
      } else {
        locations.push(obj);
      }
      saveLocations(locations);
      renderLocationsList(); // refresh teacher list
      alert('Saved');
    });
    document.getElementById('clearAll').addEventListener('click', (ev)=>{ ev.preventDefault(); if(confirm('Clear all locations?')){ locations=[]; saveLocations(locations); renderLocationsList(); renderList(); } });
    renderLocationsList();
  }

  function renderLocationsList(){
    const el = document.getElementById('locList');
    if(!el) return;
    el.innerHTML='';
    locations.forEach(l=>{
      const row = document.createElement('div'); row.className='result';
      row.innerHTML = `<div class="icon">${emojiFor(l.sport)}</div><div class="details"><h4>${escapeHtml(l.name)} <small style="color:var(--muted)">(${escapeHtml(l.id)})</small></h4><p class="muted">${escapeHtml(l.sport)} · ${escapeHtml(l.details)}</p></div><div style="margin-left:auto"><button class="btn" data-id="${escapeHtml(l.id)}">Edit</button></div>`;
      el.appendChild(row);
      row.querySelector('button').addEventListener('click', ()=>{
        document.getElementById('locId').value = l.id;
        document.getElementById('locName').value = l.name;
        document.getElementById('locFloor').value = l.details;
        document.getElementById('locSport').value = l.sport;
        document.getElementById('teacherName').value = l.teacher;
        document.getElementById('teacherContact').value = l.contact;
        document.getElementById('photoUrl').value = (l.photos && l.photos[0])||'';
        document.getElementById('changeFreq').value = l.freq||'semester';
      });
    });
  }

  // Student auth / save examples (very simple local-only auth)
  const stuSignUp = document.getElementById('stuSignUp');
  if(stuSignUp) stuSignUp.addEventListener('click', (e)=>{
    e.preventDefault();
    const name = document.getElementById('stuName').value.trim();
    const email = document.getElementById('stuEmail2').value.trim();
    const pw = document.getElementById('stuPassword2').value;
    if(!email || !pw) return document.getElementById('stuMsg2').textContent='Please enter email & password';
    const users = JSON.parse(localStorage.getItem('fmpe_users')||'[]');
    if(users.find(u=>u.email===email)) return document.getElementById('stuMsg2').textContent='User exists';
    users.push({name,email,pw,saved:[]});
    localStorage.setItem('fmpe_users', JSON.stringify(users));
    document.getElementById('stuMsg2').textContent='Account created — sign in now';
  });
  const stuSignIn = document.getElementById('stuSignIn');
  if(stuSignIn) stuSignIn.addEventListener('click', (e)=>{
    e.preventDefault();
    const email = document.getElementById('stuEmail').value.trim();
    const pw = document.getElementById('stuPassword').value;
    const users = JSON.parse(localStorage.getItem('fmpe_users')||'[]');
    const u = users.find(x=>x.email===email && x.pw===pw);
    if(!u) return document.getElementById('stuMsg').textContent='Invalid credentials';
    document.getElementById('stuMsg').textContent='Signed in — welcome ' + (u.name||u.email);
    // load saved classes
    const savedList = document.getElementById('savedList');
    if(savedList){
      savedList.innerHTML='';
      (u.saved||[]).forEach(id=>{
        const l = locations.find(x=>x.id===id);
        if(l){ const div = document.createElement('div'); div.className='result'; div.innerHTML=`<div class="icon">${emojiFor(l.sport)}</div><div class="details"><h4>${l.name}</h4><p class="muted">${l.sport} · ${l.details}</p></div><div style="margin-left:auto"><button class="btn" data-id="${l.id}">Go</button></div>`; savedList.appendChild(div); div.querySelector('button').addEventListener('click', ()=>showLocation(l.id)); }
      });
    }
  });

  // Teacher auth (local-only, demo)
  // sign-up for teachers
  const teacherSignUp = document.getElementById('teacherSignUp');
  if(teacherSignUp) teacherSignUp.addEventListener('click', (e)=>{
    e.preventDefault();
    const name = document.getElementById('teacherNameInput').value.trim();
    const email = document.getElementById('teacherEmail').value.trim();
    const pw = document.getElementById('teacherPassword').value;
    if(!email || !pw) return document.getElementById('teacherMsg2').textContent='Please enter email & password';
    const teachers = JSON.parse(localStorage.getItem('fmpe_teachers')||'[]');
    if(teachers.find(u=>u.email===email)) return document.getElementById('teacherMsg2').textContent='User exists';
    teachers.push({name,email,pw});
    localStorage.setItem('fmpe_teachers', JSON.stringify(teachers));
    document.getElementById('teacherMsg2').textContent='Account created — redirecting to sign in...';
    setTimeout(()=> window.location.href = 'teacher-signin.html', 900);
  });

  // sign-in for teachers (redirects to teacher admin page)
  const teacherSignIn = document.getElementById('teacherSignIn');
  if(teacherSignIn) teacherSignIn.addEventListener('click', (e)=>{
    e.preventDefault();
    const email = document.getElementById('teacherEmailLogin').value.trim();
    const pw = document.getElementById('teacherPasswordLogin').value;
    const teachers = JSON.parse(localStorage.getItem('fmpe_teachers')||'[]');
    const t = teachers.find(x=>x.email===email && x.pw===pw);
    if(!t) return document.getElementById('teacherMsg').textContent='Invalid credentials';
    document.getElementById('teacherMsg').textContent='Signed in — welcome ' + (t.name||t.email);
    setTimeout(()=> window.location.href = 'teacher.html', 600);
  });

  // small nice mouse parallax for sphere
  const sphere = document.getElementById('sphere');
  document.addEventListener('mousemove', (e)=>{
    const x = (e.clientX / window.innerWidth - 0.5) * 18;
    const y = (e.clientY / window.innerHeight - 0.5) * 18;
    if(sphere) sphere.style.transform = `rotateY(${x}deg) rotateX(${y}deg)`;
  });

  // do not auto-open last viewed location on load — keep default GENERAL INFORMATIONS
  // (previous behavior loaded `fmpe_last_view` here and called showLocation)

  // Expose a simple query function for the chat UI.
  // Returns an object: { type: 'location', location } or { type: 'text', text }
  function fmpeQuery(q){
    if(!q) return {type:'text', text:'Please ask about a sport, location or teacher.'};
    const qq = q.trim().toLowerCase();
    const map = {'basketball':'basketball','🏀':'basketball','羽毛球':'badminton','badminton':'badminton','ping':'tabletennis','table':'tabletennis','乒乓':'tabletennis','ping pong':'tabletennis','swim':'swimming','游泳':'swimming'};
    for(const k in map){ if(qq.includes(k)){ const loc = locations.find(l=>l.sport && l.sport.toLowerCase().includes(map[k])); if(loc) return {type:'location', location:loc}; } }
    const teacherMatch = locations.find(l => (l.teacher||'').toLowerCase().includes(qq));
    if(teacherMatch) return {type:'location', location: teacherMatch};
    const idMatch = locations.find(l => l.id.toLowerCase()===qq || l.name.toLowerCase()===qq);
    if(idMatch) return {type:'location', location: idMatch};
    return {type:'text', text: 'I could not find a matching location. Try asking for a sport (e.g. "basketball") or a location id.'};
  }

  // expose globally
  window.fmpeQuery = fmpeQuery;

})();
