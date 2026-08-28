const audio=document.getElementById('audio');
const cover=document.getElementById('cover'), titleEl=document.getElementById('title'), artistEl=document.getElementById('artist'), albumEl=document.getElementById('album');
const progress=document.getElementById('progress'), currentEl=document.getElementById('current'), durationEl=document.getElementById('duration'), list=document.getElementById('list');
let library=[], queue=[], current=-1, shuffle=false, repeat=false, tab='queue';

const saved=JSON.parse(localStorage.getItem('termuxflac')||'{}');
queue=saved.queue||[]; current=saved.current??-1; shuffle=!!saved.shuffle; repeat=!!saved.repeat;

function fmt(s){if(!isFinite(s))return'0:00';s=Math.max(0,Math.floor(s));return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
function save(){localStorage.setItem('termuxflac',JSON.stringify({queue,current,shuffle,repeat}))}
function setMedia(t){
 titleEl.textContent=t?.title||'Nothing playing'; artistEl.textContent=t?.artist||'Choose a track'; albumEl.textContent=t?.album||'';
 cover.src=t?.art||'/api/art/default';
 if(t) navigator.mediaSession&&(navigator.mediaSession.metadata=new MediaMetadata({title:t.title,artist:t.artist||'',album:t.album||'',artwork:[{src:location.origin+t.art,sizes:'512x512',type:'image/jpeg'}]}));
}
function render(){
 const data=tab==='queue'?queue:library;
 list.innerHTML='';
 if(!data.length){list.innerHTML='<div class="empty">No tracks here.</div>';return}
 data.forEach((t,i)=>{
   const qIndex=tab==='queue'?i:queue.findIndex(x=>x.id===t.id);
   const row=document.createElement('div'); row.className='row '+(qIndex===current&&tab==='queue'?'playing':'');
   row.innerHTML=`<img src="${t.art}" loading="lazy"><div><div class="name">${esc(t.title)}</div><div class="sub">${esc(t.artist||'Unknown')} · ${esc(t.album||'')}</div></div><div class="actions"><button title="Play">▶</button><button title="Add">＋</button></div>`;
   row.querySelectorAll('button')[0].onclick=()=>playAt(tab==='queue'?i:qIndex>=0?qIndex:-1,t);
   row.querySelectorAll('button')[1].onclick=()=>{queue.push(t);save();render()};
   list.appendChild(row);
 })
}
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
async function load(){
 const r=await fetch('/api/library'); library=await r.json();
 if(queue.length){queue=queue.map(q=>library.find(t=>t.id===q.id)).filter(Boolean)}
 render(); save();
 if(current>=0&&queue[current]) setMedia(queue[current]);
}
async function playAt(i, t){
 if(t && (i<0||i>=queue.length)){queue.push(t);i=queue.length-1}
 if(i<0)return;
 current=i; const tr=queue[current]; setMedia(tr); audio.src=tr.stream; await audio.play(); save(); render();
}
function next(){
 if(!queue.length)return;
 if(shuffle&&queue.length>1){let n;do n=Math.floor(Math.random()*queue.length);while(n===current);current=n}
 else current=(current+1)%queue.length;
 if(!repeat||current!==0) playAt(current); else playAt(current);
}
function prev(){if(audio.currentTime>3){audio.currentTime=0;return}current=(current-1+queue.length)%queue.length;playAt(current)}
document.getElementById('play').onclick=()=>audio.paused?audio.play():audio.pause();
document.getElementById('next').onclick=next;document.getElementById('prev').onclick=prev;
document.getElementById('shuffle').onclick=e=>{shuffle=!shuffle;e.currentTarget.classList.toggle('active',shuffle);save()};
document.getElementById('repeat').onclick=e=>{repeat=!repeat;e.currentTarget.classList.toggle('active',repeat);save()};
audio.onplay=()=>document.getElementById('play').textContent='⏸';
audio.onpause=()=>document.getElementById('play').textContent='▶';
audio.ontimeupdate=()=>{progress.value=audio.duration?audio.currentTime/audio.duration*100:0;currentEl.textContent=fmt(audio.currentTime)};
audio.onloadedmetadata=()=>durationEl.textContent=fmt(audio.duration);
audio.onended=()=>{if(repeat){audio.currentTime=0;audio.play()}else next()};
progress.oninput=()=>{if(audio.duration)audio.currentTime=progress.value/100*audio.duration};
document.getElementById('search').oninput=async e=>{const q=e.target.value.trim();if(!q){render();return}const r=await fetch('/api/library?q='+encodeURIComponent(q));library=await r.json();tab='library';document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x.dataset.tab===tab));render()};
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{tab=b.dataset.tab;document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));render()});
document.getElementById('scanBtn').onclick=async()=>{document.getElementById('scanBtn').textContent='…';await fetch('/api/scan',{method:'POST'});await load();document.getElementById('scanBtn').textContent='↻'};
if('mediaSession'in navigator){navigator.mediaSession.setActionHandler('play',()=>audio.play());navigator.mediaSession.setActionHandler('pause',()=>audio.pause());navigator.mediaSession.setActionHandler('nexttrack',next);navigator.mediaSession.setActionHandler('previoustrack',prev)}
document.getElementById('shuffle').classList.toggle('active',shuffle);document.getElementById('repeat').classList.toggle('active',repeat);
load();
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/sw.js")
            .then(() => console.log("TermuxFLAC PWA ready"))
            .catch(err => console.error("PWA error:", err));
    });
}
