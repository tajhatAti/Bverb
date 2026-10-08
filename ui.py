"""ui.py - website (notun UI v2)"""
HTML = r"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Group Moderator Pro</title>
<style>
  :root{
    --bg:#0b0e14;--bg2:#0f1320;--panel:#141a28;--panel2:#1a2133;--line:#232c42;
    --text:#e9edf7;--muted:#8b95ad;--ok:#34d399;--warn:#fbbf24;--err:#f87171;--info:#60a5fa;
    --acc:#7c5cff;--acc2:#22d3ee;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{background:radial-gradient(1200px 600px at 10% -10%,#1a1440 0%,transparent 60%),
       radial-gradient(1000px 500px at 110% 0%,#0b2d3d 0%,transparent 55%),var(--bg);
       color:var(--text);font-family:"Segoe UI",system-ui,"Noto Sans Bengali",sans-serif;line-height:1.5;min-height:100vh}
  a{color:var(--info)}
  .wrap{display:flex;gap:16px;max-width:1280px;margin:0 auto;padding:16px}
  /* ---------- sidebar ---------- */
  .side{width:212px;flex:0 0 212px;position:sticky;top:16px;align-self:flex-start}
  .brand{display:flex;align-items:center;gap:10px;padding:10px 12px;margin-bottom:12px}
  .brand .logo{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;font-size:20px;
    background:linear-gradient(135deg,var(--acc),var(--acc2));box-shadow:0 6px 20px rgba(124,92,255,.35)}
  .brand b{font-size:15px;display:block}
  .brand small{color:var(--muted);font-size:11.5px}
  .nav{display:flex;flex-direction:column;gap:4px}
  .nav button{display:flex;align-items:center;gap:9px;background:transparent;border:0;color:var(--muted);
    padding:10px 12px;border-radius:11px;font-size:13.5px;font-weight:600;cursor:pointer;text-align:left;width:100%}
  .nav button:hover{background:var(--panel);color:var(--text)}
  .nav button.on{background:linear-gradient(135deg,rgba(124,92,255,.22),rgba(34,211,238,.14));
    color:var(--text);box-shadow:inset 0 0 0 1px var(--line)}
  .nav .ic{font-size:16px;width:20px;text-align:center}
  .main{flex:1;min-width:0}
  /* ---------- cards ---------- */
  .card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
    border-radius:16px;padding:14px;margin-bottom:12px}
  .card h2{font-size:15px;margin:0 0 10px;display:flex;align-items:center;gap:8px}
  .card h3{font-size:12.5px;margin:14px 0 6px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
  .muted{color:var(--muted);font-size:12.5px}
  .row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  .between{justify-content:space-between}
  .grow{flex:1;min-width:120px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
  .grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
  .grid4{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
  /* ---------- controls ---------- */
  input[type=text],input[type=number],input[type=password],select,textarea{
    width:100%;background:#0a0d15;color:var(--text);border:1px solid var(--line);border-radius:10px;
    padding:9px 10px;font-size:13.5px;font-family:inherit}
  textarea{min-height:80px;resize:vertical;font-size:12.5px}
  input:focus,select:focus,textarea:focus{outline:2px solid rgba(96,165,250,.5);outline-offset:1px}
  label{display:block;font-size:12px;color:var(--muted);margin:6px 0 3px}
  button{background:#232c42;color:var(--text);border:1px solid var(--line);border-radius:10px;
    padding:9px 14px;font-size:13.5px;font-weight:700;cursor:pointer;font-family:inherit}
  button:hover{filter:brightness(1.15)}
  button:disabled{opacity:.5;cursor:default}
  button.pri{background:linear-gradient(135deg,var(--acc),#5b8cff);border-color:transparent;color:#fff}
  button.ok{background:linear-gradient(135deg,#0f8a5f,#10b981);border-color:transparent;color:#eafff5}
  button.dan{background:#4a1f26;border-color:#6b2b36;color:#ffd6d6}
  button.sm{padding:6px 10px;font-size:12px;border-radius:9px}
  button.ghost{background:transparent}
  .sw{display:inline-flex;align-items:center;gap:8px;cursor:pointer;user-select:none;font-size:13px}
  .sw input{display:none}
  .sw .tk{width:38px;height:21px;border-radius:99px;background:#2a3450;position:relative;transition:.18s;flex:0 0 38px}
  .sw .tk:after{content:"";position:absolute;top:2.5px;left:3px;width:16px;height:16px;border-radius:50%;
    background:#93a0bd;transition:.18s}
  .sw input:checked+.tk{background:linear-gradient(135deg,#0ea572,#34d399)}
  .sw input:checked+.tk:after{left:19px;background:#fff}
  .chk{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--text);margin:5px 0;cursor:pointer}
  .chk input{width:16px;height:16px;accent-color:#7c5cff}
  /* ---------- misc ---------- */
  .badge{display:inline-flex;align-items:center;gap:6px;padding:4px 11px;border-radius:99px;font-size:12px;font-weight:700}
  .b-ready{background:rgba(52,211,153,.15);color:var(--ok)}
  .b-need_session{background:rgba(96,165,250,.15);color:var(--info)}
  .b-connecting{background:rgba(251,191,36,.15);color:var(--warn)}
  .chip{display:inline-flex;align-items:center;gap:4px;background:#1d2438;border:1px solid var(--line);
    border-radius:99px;padding:2px 9px;font-size:11.5px;color:var(--muted);margin:2px 4px 0 0}
  .chip.g{color:var(--ok);border-color:rgba(52,211,153,.3)}
  .chip.r{color:var(--err);border-color:rgba(248,113,113,.3)}
  .chip.y{color:var(--warn);border-color:rgba(251,191,36,.3)}
  .stat{text-align:center;padding:12px 8px}
  .stat b{display:block;font-size:22px;line-height:1.2}
  .stat span{color:var(--muted);font-size:11.5px}
  .log{border-left:3px solid var(--line);padding:7px 10px;margin-bottom:6px;background:#111726;border-radius:0 10px 10px 0;font-size:13px}
  .log.action{border-color:var(--ok)} .log.error{border-color:var(--err)} .log.cancel,.log.dry,.log.limit{border-color:var(--warn)}
  .log.note{border-color:var(--info)} .log.blacklist{border-color:#e879f9} .log.bad{border-color:var(--err)}
  .act{background:#0e1420;border:1px solid var(--line);border-radius:12px;padding:10px;margin-top:8px}
  .msg{font-size:13px;margin-top:6px;min-height:18px} .msg.g{color:var(--ok)} .msg.e{color:var(--err)}
  .sec{border:1px solid var(--line);border-radius:12px;margin-top:8px;background:#0e1420;overflow:hidden}
  .sec>summary{cursor:pointer;padding:10px 12px;font-size:13.5px;font-weight:700;list-style:none;display:flex;gap:8px;align-items:center}
  .sec>summary::-webkit-details-marker{display:none}
  .sec>summary:after{content:"＋";margin-left:auto;color:var(--muted)}
  .sec[open]>summary:after{content:"－"}
  .sec>div{padding:2px 12px 12px}
  .hide{display:none !important}
  .bar{height:6px;border-radius:99px;background:#202940;overflow:hidden}
  .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--acc),var(--acc2))}
  .toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#1c2334;border:1px solid var(--line);
    padding:10px 18px;border-radius:12px;font-size:13px;z-index:99;box-shadow:0 10px 30px rgba(0,0,0,.5);max-width:92%}
  .hline{display:flex;align-items:center;gap:10px;padding:9px 10px;border:1px solid var(--line);border-radius:12px;
    background:#101622;margin-bottom:7px}
  .hline .t{flex:1;min-width:0}.hline .t b{display:block;font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .split{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .big{font-size:26px}
  @media(max-width:860px){
    .wrap{flex-direction:column;padding:10px}
    .side{width:100%;flex:auto;position:static}
    .nav{flex-direction:row;overflow-x:auto;padding-bottom:4px}
    .nav button{white-space:nowrap}
    .nav .ic{display:none}
    .split,.grid2{grid-template-columns:1fr}
  }
</style>
</head>
<body>
<div class="wrap">
  <aside class="side">
    <div class="brand">
      <div class="logo">🛡️</div>
      <div><b>Moderator Pro</b><small id="who">connect koro</small></div>
    </div>
    <div class="nav" id="nav"></div>
    <div class="card" style="margin-top:12px">
      <div class="row between"><span class="muted">Status</span><span id="badge" class="badge b-need_session">…</span></div>
      <div id="sideinfo" class="muted" style="margin-top:8px"></div>
    </div>
  </aside>
  <main class="main" id="main"></main>
</div>
<div id="toast" class="toast hide"></div>

<script>
/* ============================= helper ============================= */
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtT = t => t ? new Date(t*1000).toLocaleString() : "";
const CLIP = (s,n) => { s = String(s==null?"":s); return s.length>n ? s.slice(0,n-1)+"…" : s; };
const ACT_BN = {ban:"Ban",mute:"Mute",unban:"Unban",unmute:"Unmute",kick:"Kick",warn:"Warn",unwarn:"Unwarn",
  delete:"Message delete",delete_all:"Sob message delete",promote:"Admin banano",demote:"Admin theke namao",
  add_to_group:"Onno group e add",dm:"DM pathao",reply:"Group e reply",pin:"Pin",unpin:"Unpin",
  restrict:"Restrict (shudhu dekhte parbe)",lock:"Group lock",unlock:"Group unlock",slowmode:"Slowmode",
  purge:"Message purge",gban:"Sob group e ban",ungban:"Sob group theke unban"};
const PERMS = [["send_messages","Message"],["send_media","Media"],["send_stickers","Sticker"],["send_gifs","GIF"],
  ["send_polls","Poll"],["embed_link_previews","Link preview"],["invite_users","Invite"],["pin_messages","Pin"],["change_info","Group info"]];
const LOCKS = [["mention","@mention"],["hashtag","#hashtag"],["email","Email"],["phone","Phone no."],
  ["long","Lomba message"],["emoji","Onek emoji"],["inline_buttons","Inline button"],["via_bot","Inline bot"],
  ["forward","Forward"],["photo","Chhobi"],["video","Video"],["sticker","Sticker"],["gif","GIF"],["voice","Voice"],
  ["video_note","Gol video"],["audio","Audio"],["document","File"],["poll","Poll"],["contact","Contact"],
  ["location","Location"],["game","Game"]];
const LOCK_NAMES = LOCKS.map(x=>x[0]);
const RIGHTS = [["delete_messages","Message delete"],["ban_users","Ban/Mute"],["invite_users","Invite"],["pin_messages","Pin"],
  ["change_info","Group info"],["add_admins","Admin banano"],["manage_call","Voice chat"],["anonymous","Anonymous"]];
const MODES = [["strike","🔁 Dhap dhap (warn → mute → ban)"],["delete","🗑️ Shudhu delete"],["warn","⚠️ Delete + warn"],
  ["mute","🔇 Delete + mute"],["kick","👢 Delete + kick"],["ban","⛔ Delete + ban"]];

let S = null, G = null, R = null, TR = null, PR = "", ST = null;
let tab = "dashboard", inited = {rules:false,people:false,settings:false,shield:false};
let openG = {}, gFilter = "", busy = false, logFilter = "all", logQ = "";

async function api(path, body){
  const r = body === undefined ? await fetch(path) : await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  try{ return await r.json(); }catch(e){ return {ok:false,error:"Server response thik na"}; }
}
function toast(t, bad){
  const el = $("toast"); el.textContent = t; el.style.color = bad ? "var(--err)" : "var(--text)";
  el.classList.remove("hide"); clearTimeout(toast.t); toast.t = setTimeout(()=>el.classList.add("hide"), 4000);
}
function ask(t){ return confirm(t); }

/* ============================= nav ============================= */
const TABS = [["dashboard","🏠","Dashboard"],["groups","💬","Groups"],["shield","🛡️","Link Shield"],
  ["rules","⚡","Rules"],["people","👥","People"],["log","📜","Log"],["settings","⚙️","Settings"]];
function renderNav(){
  $("nav").innerHTML = TABS.map(([k,ic,n]) => `<button class="${k===tab?"on":""}" onclick="showTab('${k}')"><span class="ic">${ic}</span>${n}</button>`).join("");
}
function showTab(t){
  tab = t; renderNav();
  if(t === "groups" && !G) loadGroups();
  if(t === "rules" && !G) loadGroups(true);
  if(t === "shield" && !G) loadGroups(true);
  render();
}
function badge(){
  $("badge").textContent = S.status === "ready" ? "ONLINE" : S.status.replace("_"," ");
  $("badge").className = "badge b-" + S.status;
  $("who").textContent = S.me ? S.me : "session nai";
  const st = S.stats && S.stats.today || {};
  $("sideinfo").innerHTML = `👥 ${G?G.length:"?"} group · 🔗 ${st.links||0} link dhora<br>🕒 ${fmtT(S.started)} theke chalu`;
}

/* ============================= dashboard ============================= */
function tile(v, l, color){
  return `<div class="card stat" style="margin:0"><b style="color:${color||"var(--text)"}">${v}</b><span>${l}</span></div>`;
}
function renderDashboard(){
  let h = "";
  if(!S.me || S.status !== "ready"){
    h += `<div class="card"><h2>🔑 Session connect koro</h2>
      <div class="muted">Telethon session string paste kore Connect chap dao. Ei session diyei sob group modarate hobe.</div>
      <textarea id="sess" placeholder="1BVts..." spellcheck="false" style="margin-top:8px"></textarea>
      <div class="row" style="margin-top:8px"><button class="pri" id="cbtn" onclick="connect()">🔌 Connect</button>
      <span class="muted">${esc(S.error||"")}</span></div></div>`;
  }else{
    const st = S.stats.today || {}, tot = S.stats.total || {};
    h += `<div class="grid4" style="margin-bottom:12px">
      ${tile(G?G.length:"…", "Group", "var(--info)")}
      ${tile(st.links||0, "Aj link dhora")}
      ${tile(st.deleted||0, "Message delete", "var(--ok)")}
      ${tile(st.mutes||0, "Mute", "var(--warn)")}
      ${tile(st.bans||0, "Ban/Kick", "var(--err)")}
      ${tile((S.blacklist||[]).length, "Blacklist", "#e879f9")}
      ${tile(tot.links||0, "Sob miliye link")}
      ${tile(S.locks_active||0, "Lock chalu", "var(--warn)")}
    </div>`;
    h += `<div class="card"><h2>⚡ Duto click er kaj</h2>
      <div class="row">
        <button class="ok" onclick="bulkSet('link_guard.on',true)">🛡️ Sob group e Link Ban CHALU</button>
        <button class="ghost" onclick="bulkSet('link_guard.on',false)">Link Ban bondho</button>
        <button class="ghost" onclick="bulkSet('automod.enabled',true)">🤖 AutoMod sob group e chalu</button>
        <button class="ghost" onclick="bulkSet('clean.join',true)">🧹 Join/Leave message safai</button>
      </div>
      <div class="row" style="margin-top:8px">
        <button class="ghost" onclick="lockAll(true)">🔒 Sob group lock</button>
        <button class="ghost" onclick="lockAll(false)">🔓 Sob group unlock</button>
        <button class="ghost" onclick="showTab('shield')">🔍 Link test koro</button>
        <button class="ghost" onclick="speedtest()">🧪 Delete adhikar check</button>
      </div>
      <div class="msg" id="dmsg"></div>
      <h3>7 diner graph (link dhora)</h3>
      ${barChart()}
    </div>`;
    const off = (S.stats.offenders||[]).slice(0,5);
    h += `<div class="card"><h2>😈 Sob theke beshi link diyeche</h2>` + (off.length ? off.map(o =>
        `<div class="hline"><div class="t"><b>${esc(o.name||o.id)}</b><span class="muted">${o.n} bar · id ${o.id}</span></div>
         <button class="sm dan" onclick="blAdd(${o.id},'')">🚫 Blacklist</button></div>`).join("")
      : `<div class="muted">Ekhono keu dhora poreni 🎉</div>`) + `</div>`;
  }
  const lg = S.logs.slice(0,8);
  h += `<div class="card"><h2>📜 Notun kaj</h2>` + (lg.length ? lg.map(logRow).join("") : `<div class="muted">Kichu nai</div>`)
     + `<div class="row" style="margin-top:6px"><button class="sm ghost" onclick="showTab('log')">Sob log</button>
        ${S.me?`<button class="sm ghost" onclick="logout()">🚪 Logout</button>`:""}</div></div>`;
  if(S.cryptg === false){
    h += `<div class="card"><h2>🐢 Speed tip</h2><div class="muted">cryptg install hoyni (${esc(S.cryptg_err||"")}) - pip install cryptg dile onek fast hobe.</div></div>`;
  }
  $("main").innerHTML = h;
  const keep = $("sess") ? $("sess").value : "";
  if($("sess")) $("sess").value = keep;
}
function barChart(){
  const h = (S.stats.history||[]);
  if(!h.length) return `<div class="muted">Data nai</div>`;
  const mx = Math.max(1, ...h.map(x=>x.links));
  return `<div class="row" style="align-items:flex-end;gap:6px">` + h.map(x =>
    `<div style="flex:1;text-align:center"><div class="bar" style="height:60px;display:flex;align-items:flex-end">
      <i style="width:100%;height:${Math.round((x.links/mx)*100)}%"></i></div>
      <div class="muted" style="font-size:10px">${x.day.slice(5)}</div><div style="font-size:11px">${x.links}</div></div>`).join("") + `</div>`;
}
function logRow(l){
  const cls = l.kind==="action" && l.ok===false ? "bad" : l.kind;
  return `<div class="log ${cls}"><div class="muted">${fmtT(l.t)}${l.chat_title?" · "+esc(l.chat_title):""}${l.rule?" · "+esc(l.rule):""}</div>
    <div>${l.user_name?"<b>"+esc(l.user_name)+"</b> — ":""}${esc(l.msg)}</div>
    ${l.undo&&l.ok?`<div style="margin-top:5px"><button class="sm ghost" onclick="undoIt('${l.id}')">↩ Undo</button></div>`:""}</div>`;
}
async function connect(){
  const s = $("sess").value.trim(); if(!s) return toast("Session string dao", true);
  $("cbtn").disabled = true; $("cbtn").textContent = "Connecting…";
  const r = await api("api/connect", {session:s});
  if(!r.ok) toast(r.error || "Connect hoyni", true); else { toast("Connect hoyeche ✅"); G = null; }
  await refresh(true);
}
async function logout(){ if(!ask("Logout korbe?")) return; await api("api/logout", {}); G = null; await refresh(true); }
async function undoIt(id){ const r = await api("api/undo", {id}); toast(r.msg||"", !r.ok); refresh(true); }
async function lockAll(on){
  if(!ask(on ? "Sob group lock korbe?" : "Sob group unlock korbe?")) return;
  const r = await api("api/bulk_lock", {lock:on});
  toast(r.ok ? `${r.n} ta group e ${on?"lock":"unlock"} holo` : (r.error||"Hoyni"), !r.ok);
  G = null; refresh(true);
}
async function bulkSet(key, val){
  const r = await api("api/bulk", {key, value:val});
  if(!r.ok) return toast(r.error||"Hoyni", true);
  toast(`${r.n} ta group e ${val?"CHALU":"BONDHO"} kora hoyeche`);
  G = null; refresh(true);
}
async function speedtest(){
  const r = await api("api/speedtest");
  if(!r.ok) return toast(r.error, true);
  const bad = r.groups.filter(g=>!g.delete);
  toast(bad.length ? `${bad.length} ta group e delete adhikar nei!` : "Sob group e delete adhikar ache ✅", !!bad.length);
}
async function blAdd(id, name){
  const r = await api("api/blacklist", {id, name});
  toast(r.ok ? `${name||id} blacklist e gelo 🚫` : (r.error||"Hoyni"), !r.ok); refresh(true);
}

/* ============================= groups ============================= */
async function loadGroups(force){
  const r = await api("api/groups" + (force?"?force=1":""));
  if(!r.ok){ toast(r.error || "Group list ashe ni", true); G = []; return render(); }
  G = r.groups; render();
}
function chipsFor(g){
  const x = g.rights||{}, c = [];
  c.push(g.creator ? '<span class="chip g">👑 Owner</span>' : g.admin ? '<span class="chip g">Admin</span>' : '<span class="chip r">Admin na</span>');
  for(const [k,n] of [["ban_users","Ban"],["delete_messages","Delete"],["pin_messages","Pin"],["invite_users","Invite"]])
    if(g.admin) c.push(`<span class="chip ${x[k]?"g":"y"}">${n}</span>`);
  return c.join("");
}
function sw(chat, key, val, label){
  return `<label class="sw" title="${esc(label||"")}"><input type="checkbox" ${val?"checked":""}
    onchange="quickSet(${chat},'${key}',this.checked)"><span class="tk"></span><span class="muted">${esc(label||"")}</span></label>`;
}
function renderGroups(){
  if(!G){ $("main").innerHTML = `<div class="card"><div class="muted">Group load hocche… (session connect koro)</div></div>`; return; }
  const q = gFilter.toLowerCase();
  const list = G.filter(g => (!q || (g.title||"").toLowerCase().includes(q)));
  let h = `<div class="card"><h2>💬 Groups <span class="muted">(${list.length}/${G.length})</span></h2>
    <div class="row"><input type="text" class="grow" placeholder="🔍 Group khujo…" value="${esc(gFilter)}" oninput="gFilter=this.value;renderGroups()">
      <button class="ghost" onclick="loadGroups(true)">🔄 Refresh</button>
      <button class="ghost" onclick="showTab('shield')">🛡️ Link Shield</button></div></div>`;
  if(!list.length) h += `<div class="card muted">Kono group paoa jayni</div>`;
  for(const g of list){
    const o = openG[g.id]||"", c = g.cfg, lgd = (c.link_guard||{});
    h += `<div class="card" id="g_${g.id}">
      <div class="row between"><div class="t" style="flex:1;min-width:180px">
        <b>${esc(g.title)}</b><div class="muted">${g.members||"?"} member · id ${g.id}</div></div>
        ${sw(g.id,"enabled",c.enabled,"Chalu")}</div>
      <div>${chipsFor(g)}${lgd.on?'<span class="chip g">🛡️ Link Ban</span>':'<span class="chip r">🛡️ Link Ban off</span>'}
        ${c.automod.enabled?'<span class="chip g">🤖 AutoMod</span>':""}
        ${c.welcome.on?'<span class="chip g">👋 Welcome</span>':""}
        ${c.captcha.on?'<span class="chip g">🧩 Captcha</span>':""}
        ${c.night.on?'<span class="chip g">🌙 Night</span>':""}
        ${S.locked_chats.includes(String(g.id))?'<span class="chip y">🔒 Locked</span>':""}</div>
      <div class="row" style="margin-top:9px">
        ${sw(g.id,"link_guard.on",lgd.on,"Link Ban")}
        ${sw(g.id,"automod.enabled",c.automod.enabled,"AutoMod")}
        ${sw(g.id,"welcome.on",c.welcome.on,"Welcome")}
        ${sw(g.id,"antibot.on",c.antibot.on,"Anti-Bot")}
      </div>
      <div class="row" style="margin-top:9px">
        <button class="sm pri" onclick="gOpen(${g.id},'set')">⚙️ Settings</button>
        <button class="sm ghost" onclick="gOpen(${g.id},'mem')">👥 Members</button>
        <button class="sm ghost" onclick="doAct(${g.id},0,{type:'lock',perms:{}})">🔒 Lock</button>
        <button class="sm ghost" onclick="doAct(${g.id},0,{type:'unlock'})">🔓 Unlock</button>
        <button class="sm ghost" onclick="doAct(${g.id},0,{type:'purge',num:50})">🧹 Purge 50</button>
      </div>
      <div id="gx_${g.id}">${o==="set" ? gForm(g) : o==="mem" ? gMembers(g) : ""}</div></div>`;
  }
  $("main").innerHTML = h;
  for(const g of list) if(openG[g.id]==="mem") memLoad(g.id);
}
function gOpen(id, what){ openG[id] = openG[id]===what ? "" : what; renderGroups(); }
async function quickSet(chat, key, val){
  const r = await api("api/quick", {chat, key, value:val});
  if(!r.ok) return toast(r.error||"Hoyni", true);
  const g = (G||[]).find(x=>x.id===chat); if(g) g.cfg = r.cfg;
  toast("Save hoyeche ✅");
  // form khola thakle abar render korbo na (likha muchhe jabe)
  if(!Object.values(openG).some(Boolean)) render();
}
/* ---- group settings form ---- */
function gv(g, path){ return path.split(".").reduce((o,k)=>o==null?undefined:o[k], g.cfg); }
const fb=(g,p,l)=>`<label class="chk"><input type="checkbox" data-g="${g.id}" data-p="${p}" data-t="b" ${gv(g,p)?"checked":""}> ${l}</label>`;
const fn=(g,p,l)=>`<div><label>${l}</label><input type="number" data-g="${g.id}" data-p="${p}" data-t="n" value="${gv(g,p)}"></div>`;
const ft=(g,p,l)=>`<div><label>${l}</label><input type="text" data-g="${g.id}" data-p="${p}" data-t="t" value="${esc(gv(g,p))}"></div>`;
const fa=(g,p,l,val,h)=>`<label>${l}</label><textarea style="min-height:${h||60}px" data-g="${g.id}" data-p="${p}" data-t="ta">${esc(val==null?"":val)}</textarea>`;
const fs=(g,p,l,opts)=>`<div><label>${l}</label><select data-g="${g.id}" data-p="${p}" data-t="s">` +
  opts.map(([v,n])=>`<option value="${v}" ${String(v)===String(gv(g,p))?"selected":""}>${n}</option>`).join("")+`</select></div>`;
const sec=(t,inner,open)=>`<details class="sec" ${open?"open":""}><summary>${t}</summary><div>${inner}</div></details>`;
function gForm(g){
  const c = g.cfg, am = c.automod, lg = c.link_guard;
  const shield = `${fb(g,"link_guard.on","<b>Link Shield chalu</b> (jekono link sathe sathe delete)")}
    <div class="grid2">${fs(g,"link_guard.mode","Link dile ki hobe",MODES)}${fn(g,"link_guard.ban_after","Koybar por direct ban (0 = na)")}</div>
    <div class="grid2">${fn(g,"link_guard.mute_min","Mute koto minit")}${fn(g,"link_guard.notice_s","Warning koto sec pore muchbe")}</div>
    ${fb(g,"link_guard.exempt_admins","Group er admin ra link dite parbe")}
    <div class="grid2">${fb(g,"link_guard.block_buttons","Inline URL button wala message o delete")}
    ${fb(g,"link_guard.block_edits","Edit kore link bosaleo dhora porbe")}
    ${fb(g,"link_guard.block_forward","Forward kora link o delete")}</div>
    ${fa(g,"link_guard.steps","Dhap dhap shasti (ek line e ekta: warn / mute 120 / kick / ban)",lg.steps.map(s=>s.action+(s.mute_min?" "+s.mute_min:"")).join("\n"),60)}
    ${fa(g,"link_guard.notice","Group e ja dekhabe ({name} {n} {max} {link} {group})",lg.notice,60)}
    ${fa(g,"link_guard.allow","Ei domain gulor link delete hobe na (ek line e ekta)",(lg.allow||[]).join("\n"),60)}`;
  const lockSel = `<div><label>Lock bhangle ki hobe (ban/mute/delete)</label><select data-g="${g.id}" data-t="lockact">` +
    [["strike","Dhap dhap (warn → mute)"],["delete","Shudhu muche felo"],["mute","Mute"],["ban","Ban"]]
      .map(([v,n])=>`<option value="${v}" ${am.locks.mention.action===v?"selected":""}>${n}</option>`).join("")+`</select></div>`;
  const locks = `${fb(g,"automod.enabled","<b>AutoMod chalu</b>")}<h3>Ki ki dewa jabe na (tick = block)</h3>
    <div class="grid3">${LOCKS.map(([k,n])=>fb(g,`automod.locks.${k}.on`,n)).join("")}</div>${lockSel}
    <div class="grid2">${fn(g,"automod.long_max","Lomba = koto akkhor+")}${fn(g,"automod.emoji_max","Onek emoji = koyta+")}</div>`;
  const st = am.strikes;
  const strikes = `<div class="muted">Prothom bar = hushiyar, tarpor mute. Prottek line: warn / mute 60 / kick / ban</div>
    ${fa(g,"automod.strikes.steps","Dhap gulo",st.steps.map(s=>s.action+(s.mute_min?" "+s.mute_min:"")).join("\n"),60)}
    <div class="grid2">${fn(g,"automod.strikes.window_h","Koto ghonta er dhap gona hobe")}${fn(g,"automod.strikes.notify_delete_s","Hushiyar message koto sec pore muchbe")}</div>
    ${ft(g,"automod.strikes.warn_text","Hushiyar message ({name} {kind} {n} {max})")}`;
  const wf = `${fb(g,"automod.words.on","Nishiddho shobdo block")}
    ${fa(g,"automod.words.list","Shobdo (ek line e ekta, regex hole re: diye shuru)",am.words.list.join("\n"),60)}
    ${fs(g,"automod.words.action","Shobdo e shasti",[["strike","Dhap dhap"],["delete","Shudhu delete"],["mute","Mute"],["ban","Ban"]])}
    ${fb(g,"automod.flood.on","Flood (druto druto message)")}
    <div class="grid2">${fn(g,"automod.flood.count","Koyta message")}${fn(g,"automod.flood.seconds","Koto sec e")}</div>${fn(g,"automod.flood.mute_min","Mute koto minit")}`;
  const join = `${fb(g,"antibot.on","Bot dhokano bondho")}
    <div class="grid2">${fs(g,"antibot.mode","Kake atkabe",[["non_admin","Admin na hole"],["everyone","Sobaike"]])}
    ${fs(g,"antibot.punish","Je add korlo tar shasti",[["none","Kichu na"],["warn","Dhap dhap"],["mute","Mute"],["ban","Ban"]])}</div>
    ${fb(g,"antiraid.on","Anti-raid (onek jon ekshathe dhukle lock)")}
    <div class="grid2">${fn(g,"antiraid.joins","Koyjon")}${fn(g,"antiraid.seconds","Koto sec e")}</div>${fn(g,"antiraid.lock_min","Lock koto minit")}
    ${fb(g,"automod.newbie.on","Notun member der link/media block")}
    <div class="grid2">${fn(g,"automod.newbie.hours","Koto ghonta")}
    ${fs(g,"automod.newbie.block","Ki block",[["links,media","Link + media"],["links","Shudhu link"],["media","Shudhu media"]])}</div>`;
  const night = `${fb(g,"night.on","Night mode (rate group lock)")}
    <div class="grid2">${ft(g,"night.from","Shuru (HH:MM)")}${ft(g,"night.to","Shesh (HH:MM)")}</div>
    ${fn(g,"night.tz","Timezone minit (Bangladesh = 360)")}
    <h3>Service message safai</h3>${fb(g,"clean.join","Join")}${fb(g,"clean.leave","Leave")}${fb(g,"clean.pin","Pin")}`;
  const wel = `${fb(g,"welcome.on","Welcome message")}${ft(g,"welcome.text","Text ({name} {group})")}${fn(g,"welcome.delete_after","Koto sec pore muchbe (0 = na)")}
    ${fb(g,"captcha.on","Captcha (bot lagbe)")}${ft(g,"captcha.text","Captcha text")}
    <div class="grid2">${fn(g,"captcha.timeout_min","Koto minit somoy")}${fs(g,"captcha.fail","Fail hole",[["kick","Kick"],["ban","Ban"]])}</div>`;
  const rules = `${fa(g,"rules_text",".rules likhle ja dekhabe",c.rules_text||"",80)}
    ${fa(g,"filters","Auto reply: ek line e  shobdo => reply",(c.filters||[]).map(f=>f.key+" => "+f.reply).join("\n"),80)}`;
  return sec("🛡️ Link Shield (link thik ei khane)", shield, true) + sec("🔒 Locks + AutoMod", locks)
    + sec("⚖️ Dhap dhap shasti", strikes) + sec("💬 Shobdo ar flood", wf)
    + sec("🤖 Bot, raid, notun member", join) + sec("🌙 Night mode ar safai", night)
    + sec("👋 Welcome ar captcha", wel) + sec("📋 Rules ar auto reply", rules)
    + `<div class="row" style="margin-top:12px"><button class="pri" onclick="gSave(${g.id})">💾 Save</button>
       <span class="muted">Save na korle auto-save hobe na</span></div><div class="msg" id="gm_${g.id}"></div>`;
}
function setP(o, path, v){
  const ks = path.split(".");
  for(let i=0;i<ks.length-1;i++) o = o[ks[i]] = o[ks[i]] || {};
  o[ks[ks.length-1]] = v;
}
async function gSave(id){
  const g = (G||[]).find(x=>x.id===id); if(!g) return;
  const cfg = {enabled:g.cfg.enabled}; let lockact = "strike";
  document.querySelectorAll(`[data-g="${id}"]`).forEach(el=>{
    const t = el.dataset.t, p = el.dataset.p; let v;
    if(t === "lockact"){ lockact = el.value; return; }
    if(!p) return;
    if(t === "b") v = el.checked;
    else if(t === "n") v = parseFloat(el.value)||0;
    else if(t === "s") v = el.value;
    else if(t === "ta"){
      if(p === "link_guard.allow") v = el.value.split("\n").map(s=>s.trim()).filter(Boolean);
      else if(p === "link_guard.steps" || p === "automod.strikes.steps")
        v = el.value.split("\n").map(s=>s.trim()).filter(Boolean).map(l=>{const a=l.split(/\s+/);return {action:a[0].toLowerCase(),mute_min:parseInt(a[1])||0};});
      else if(p === "filters")
        v = el.value.split("\n").map(s=>s.trim()).filter(Boolean).map(l=>{const i=l.indexOf("=>");return i<0?null:{key:l.slice(0,i).trim(),reply:l.slice(i+2).trim()};}).filter(Boolean);
      else v = el.value;
    } else v = el.value;
    setP(cfg, p, v);
  });
  cfg.automod = cfg.automod || {}; cfg.automod.locks = cfg.automod.locks || {};
  for(const n of LOCK_NAMES){ cfg.automod.locks[n] = cfg.automod.locks[n]||{}; cfg.automod.locks[n].action = lockact; }
  const r = await api("api/group_save", {chat:id, cfg});
  const m = $("gm_"+id);
  if(r.ok){ g.cfg = r.cfg; toast("Save hoyeche ✅"); if(m){m.className="msg g"; m.textContent="Save hoyeche ✅";} renderGroups(); }
  else { toast(r.error, true); if(m){m.className="msg e"; m.textContent=r.error||"Save hoyni";} }
}
function gMembers(g){
  return `<h3>👥 Members</h3><div class="row"><input type="text" class="grow" id="mq_${g.id}" placeholder="Nam ba @username">
    <button class="sm" onclick="memLoad(${g.id})">🔍 Khujo</button></div><div id="ml_${g.id}" class="muted" style="margin-top:8px">Load hocche…</div>`;
}
async function memLoad(id){
  const q = ($("mq_"+id)||{}).value || "";
  const r = await api(`api/members?chat=${id}&q=${encodeURIComponent(q)}`);
  const el = $("ml_"+id); if(!el) return;
  if(!r.ok){ el.textContent = r.error; return; }
  el.innerHTML = r.members.length ? r.members.map(m=>`<div class="hline">
    <div class="t"><b>${esc(m.name)}</b><span class="muted">${m.username?"@"+esc(m.username)+" · ":""}${m.id}${m.warns?" · "+m.warns+" warn":""}${m.links?" · "+m.links+" link":""}</span></div>
    ${m.admin?'<span class="chip g">Admin</span>':""}${m.bot?'<span class="chip">Bot</span>':""}
    ${m.blacklisted?'<span class="chip r">🚫 Blacklist</span>':""}
    <div class="row">
      <button class="sm dan" onclick="doAct(${id},${m.id},{type:'mute',duration_min:60})">Mute 1h</button>
      <button class="sm dan" onclick="doAct(${id},${m.id},{type:'ban'})">Ban</button>
      <button class="sm ghost" onclick="doAct(${id},${m.id},{type:'warn'})">Warn</button>
      <select style="width:auto" onchange="moreAct(${id},${m.id},this)"><option value="">Aro…</option>
        <option value="kick">Kick</option><option value="restrict">Read-only 1h</option><option value="promote">Admin banao</option>
        <option value="demote">Admin theke namao</option><option value="unban">Unban / Unmute</option><option value="gban">Sob group e ban</option>
        <option value="blacklist">🚫 Blacklist</option><option value="unblacklist">Blacklist theke tule nao</option></select></div></div>`).join("")
    : "Kono member paoa jayni";
}
function moreAct(chat, user, sel){
  const v = sel.value; sel.value=""; if(!v) return;
  if(v === "blacklist") return blAdd(user, "");
  if(v === "unblacklist"){ api("api/blacklist",{id:user,remove:true}).then(()=>{toast("Tule neoa holo");memLoad(chat);refresh(true);}); return; }
  const a = {kick:{type:"kick"}, restrict:{type:"restrict",duration_min:60,perms:{}},
    promote:{type:"promote",title:"Moderator",rights:{delete_messages:true,ban_users:true,invite_users:true,pin_messages:true}},
    demote:{type:"demote"}, unban:{type:"unban"}, gban:{type:"gban"}}[v];
  doAct(chat, user, a);
}
async function doAct(chat, user, action){
  if(["ban","kick","mute","gban","restrict","purge"].includes(action.type) && !ask((ACT_BN[action.type]||action.type)+" korbe?")) return;
  const r = await api("api/do", {chat, user, action});
  toast(r.msg || (r.ok?"Hoyeche":"Hoyni"), !r.ok); refresh(true);
}

/* ============================= link shield tab ============================= */
function renderShield(){
  const st = S.settings;
  let h = `<div class="card"><h2>🛡️ Link Shield <span class="chip g">v2</span></h2>
    <div class="muted">Link dewa matra sathe sathe delete - URL, www, t.me, wa.me, "google[.]com", "google dot com", zero-width lukaono link,
    obfuscated, inline URL button, media caption, edit kora link - sob dhora pore. Admin der link dite baron korte chaile exempt off koro.</div>
    <div class="grid3" style="margin-top:10px">
      <label class="sw"><input type="checkbox" ${st.link_guard?"checked":""} onchange="setS('link_guard',this.checked)"><span class="tk"></span>Master switch</label>
      <label class="sw"><input type="checkbox" ${st.link_notice?"checked":""} onchange="setS('link_notice',this.checked)"><span class="tk"></span>Group e warning dekhaw</label>
      <label class="sw"><input type="checkbox" ${st.link_block_edit?"checked":""} onchange="setS('link_block_edit',this.checked)"><span class="tk"></span>Edit kora link block</label>
      <label class="sw"><input type="checkbox" ${st.link_block_buttons?"checked":""} onchange="setS('link_block_buttons',this.checked)"><span class="tk"></span>Inline button link block</label>
      <label class="sw"><input type="checkbox" ${st.auto_blacklist?"checked":""} onchange="setS('auto_blacklist',this.checked)"><span class="tk"></span>Auto blacklist</label>
      <label class="sw"><input type="checkbox" ${st.link_bot_fallback?"checked":""} onchange="setS('link_bot_fallback',this.checked)"><span class="tk"></span>Bot diye delete fallback</label>
    </div>
    <div class="grid2" style="margin-top:8px">
      <div><label>Warning koto sec pore muchbe</label><input type="number" value="${st.link_notice_s}" onchange="setS('link_notice_s',+this.value)"></div>
      <div><label>Koybar link dile auto blacklist</label><input type="number" value="${st.auto_blacklist_after}" onchange="setS('auto_blacklist_after',+this.value)"></div>
    </div>
    <div class="row" style="margin-top:10px">
      <button class="ok" onclick="bulkSet('link_guard.on',true)">🛡️ Sob admin group e CHALU</button>
      <button class="ghost" onclick="bulkSet('link_guard.on',false)">Bondho koro</button>
    </div></div>`;
  /* tester */
  h += `<div class="card"><h2>🔍 Link Tester</h2>
    <div class="muted">Kono text boshao - dhora porbe kina dekho. Ekhane kichu delete hobe na.</div>
    <textarea id="ltt" placeholder="jemon: join korte  t . me / mychannel   ba   www . example . com" style="margin-top:8px"></textarea>
    <div class="row" style="margin-top:8px"><button class="pri" onclick="linkTest()">🔍 Test</button>
      <button class="ghost" onclick="$('ltt').value='https://t.me/test\u200b \u2022 google[.]com \u2022 bet365 . com'; linkTest()">Nemun boshao</button></div>
    <div id="ltout" class="msg" style="margin-top:10px"></div></div>`;
  /* per group */
  h += `<div class="card"><h2>📋 Group wise</h2>`;
  if(!G) h += `<div class="muted">Group list load hocche…</div>`;
  else if(!G.length) h += `<div class="muted">Kono group nai</div>`;
  else {
    for(const g of G.filter(x=>x.admin)){
      const lgd = g.cfg.link_guard||{};
      h += `<div class="hline"><div class="t"><b>${esc(g.title)}</b>
        <span class="muted">${ldg.on?"✅ chalu":"⛔ bondho"} · ${CLIP((MODES.find(m=>m[0]===ldg.mode)||["","?"])[1],26)} · ban @${ldg.ban_after||0}</span></div>
        <select style="width:auto" onchange="quickSet(${g.id},'link_guard.mode',this.value)">
          ${MODES.map(([v,n])=>`<option value="${v}" ${v===ldg.mode?"selected":""}>${CLIP(n,22)}</option>`).join("")}</select>
        ${sw(g.id,"link_guard.on",ldg.on,"")}</div>`;
    }
  }
  h += `</div>`;
  $("main").innerHTML = h;
}
async function setS(k, v){
  const r = await api("api/settings_save", {settings:{[k]: v}});
  if(!r.ok) return toast("Save hoyni", true);
  S.settings[k] = v; toast("Save hoyeche ✅");
}
async function linkTest(){
  const t = $("ltt").value;
  const r = await api("api/linktest", {text:t});
  const out = $("ltout");
  if(!r.ok){ out.className="msg e"; out.textContent = r.error||"Hoyni"; return; }
  if(!r.has_link){ out.className="msg g"; out.innerHTML = "✅ Kono link dhora poreni"; return; }
  out.className = "msg";
  out.innerHTML = `<div style="color:var(--ok)">🔗 ${r.count} ta link dhora poreche:</div>` +
    r.links.map(x=>`<div class="log action"><b>${esc(x.link)}</b><div class="muted">${esc(x.why)}</div></div>`).join("") +
    `<div class="muted">Normal text: ${esc(CLIP(r.normalized,300))}</div>`;
}

/* ============================= rules tab ============================= */
function rset(i,path,val){ const ks=path.split("."); let o=R[i]; for(let k=0;k<ks.length-1;k++){o[ks[k]]=o[ks[k]]||{};o=o[ks[k]];} o[ks[ks.length-1]]=val; }
function aset(i,j,k,v){ R[i].actions[j][k]=v; }
function apset(i,j,k,v){ const a=R[i].actions[j]; a.perms=a.perms||{}; a.perms[k]=v; }
function arset(i,j,k,v){ const a=R[i].actions[j]; a.rights=a.rights||{}; a.rights[k]=v; }
function rtype(i,v){ R[i].trigger = v==="reaction"?{type:"reaction",emoji:"🤬"}:{type:"command",name:"cmd"}; render(); }
function atype(i,j,v){
  const a={type:v};
  if(v==="ban") Object.assign(a,{duration_min:0,delete_history:false});
  if(v==="mute") a.duration_min=60;
  if(v==="promote") Object.assign(a,{title:"",rights:{delete_messages:true,ban_users:true,invite_users:true,pin_messages:true}});
  if(v==="add_to_group") Object.assign(a,{target_group:"",text:"Ei group e join koro: {link}"});
  if(v==="dm") a.text="Hi {name}";
  if(v==="reply") Object.assign(a,{text:"OK",delete_after:0});
  if(v==="restrict") Object.assign(a,{duration_min:60,perms:{}});
  if(v==="lock") Object.assign(a,{duration_min:0,perms:{}});
  if(v==="slowmode") a.seconds=30;
  R[i].actions[j]=a; render();
}
function addAct(i){ R[i].actions.push({type:"delete"}); render(); }
function delAct(i,j){ R[i].actions.splice(j,1); render(); }
function addRule(){ R.push({id:"r_"+Date.now(),name:"Notun rule",enabled:true,trigger:{type:"reaction",emoji:"🤬"},who:"me",groups:["*"],confirm:false,actions:[{type:"delete"}]}); render(); }
function delRule(i){ if(!ask("Rule ta muche felbe?")) return; R.splice(i,1); render(); }
function gscope(i,id,on){ let gs=R[i].groups.filter(x=>x!=="*"); id=String(id); gs=gs.filter(x=>x!==id); if(on) gs.push(id); R[i].groups=gs; }
function allScope(i,on){ R[i].groups = on?["*"]:[]; render(); }
function actHTML(a,i,j){
  let p = "";
  if(a.type==="ban") p = `<div class="grid2"><div><label>Koto minit (0 = chirokal)</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)"></div></div>
    <label class="chk"><input type="checkbox" ${a.delete_history?"checked":""} onchange="aset(${i},${j},'delete_history',this.checked)"> Oi user er sob message muchbe</label>`;
  else if(a.type==="mute") p = `<label>Koto minit (0 = jotokkhon na unmute kori)</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)">`;
  else if(a.type==="promote") p = `<label>Custom title (max 16 akkhor)</label><input type="text" value="${esc(a.title||"")}" onchange="aset(${i},${j},'title',this.value)">` +
    `<div class="grid2">` + RIGHTS.map(([k,n])=>`<label class="chk"><input type="checkbox" ${(a.rights||{})[k]?"checked":""} onchange="arset(${i},${j},'${k}',this.checked)"> ${n}</label>`).join("") + `</div>`;
  else if(a.type==="add_to_group") p = `<label>Kon group e add korbe</label><select onchange="aset(${i},${j},'target_group',this.value)"><option value="">-- bachho --</option>` +
    (G||[]).map(g=>`<option value="${g.id}" ${String(a.target_group)===String(g.id)?"selected":""}>${esc(g.title)}</option>`).join("") + `</select>
    <label>Privacy te add na hole DM e ({link})</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">`;
  else if(a.type==="restrict"||a.type==="lock") p = `<label>Koto minit (0 = ${a.type==="lock"?"jotokkhon na unlock":"chirokal"})</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)">
    <div class="muted" style="margin-top:6px">Ki ki korte parbe (kichu tick na = shudhu dekhte parbe)</div><div class="grid2">` +
    PERMS.filter(x=>a.type==="restrict"||!["invite_users","pin_messages","change_info"].includes(x[0])).map(([k,n])=>`<label class="chk"><input type="checkbox" ${(a.perms||{})[k]?"checked":""} onchange="apset(${i},${j},'${k}',this.checked)"> ${n}</label>`).join("")+`</div>`;
  else if(a.type==="slowmode") p = `<label>Second</label><select onchange="aset(${i},${j},'seconds',+this.value)">` + [0,10,30,60,300,900,3600].map(v=>`<option value="${v}" ${a.seconds===v?"selected":""}>${v?v+" sec":"bondho"}</option>`).join("")+`</select>`;
  else if(a.type==="reply") p = `<label>Text ({name} {group})</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">
    <label>Koto sec pore muchbe (0 = na)</label><input type="number" min="0" value="${a.delete_after||0}" onchange="aset(${i},${j},'delete_after',+this.value)">`;
  else if(a.type==="dm") p = `<label>Text ({name} {group})</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">`;
  return `<div class="act"><div class="row"><select class="grow" onchange="atype(${i},${j},this.value)">` +
    S.action_types.map(t=>`<option value="${t}" ${t===a.type?"selected":""}>${ACT_BN[t]||t}</option>`).join("") +
    `</select><button class="sm dan" onclick="delAct(${i},${j})">✕</button></div>${p}</div>`;
}
function ruleHTML(r,i){
  const t = r.trigger||{}, all = (r.groups||[]).includes("*");
  const trig = t.type==="reaction"
    ? `<label>Emoji (Telegram react)</label><select onchange="rset(${i},'trigger.emoji',this.value)">` +
      S.reactions.map(e=>`<option ${e===t.emoji?"selected":""}>${e}</option>`).join("")+`</select>`
    : `<label>Command nam (prefix chara)</label><input type="text" value="${esc(t.name||"")}" onchange="rset(${i},'trigger.name',this.value)">`;
  const scope = `<label class="chk"><input type="checkbox" ${all?"checked":""} onchange="allScope(${i},this.checked)"> Sob group e</label>` +
    (all?"":(G||[]).map(g=>`<label class="chk"><input type="checkbox" ${(r.groups||[]).includes(String(g.id))?"checked":""} onchange="gscope(${i},${g.id},this.checked)"> ${esc(g.title)}</label>`).join(""));
  return `<div class="card"><div class="row"><label class="sw"><input type="checkbox" ${r.enabled?"checked":""} onchange="rset(${i},'enabled',this.checked)"><span class="tk"></span></label>
      <input type="text" class="grow" value="${esc(r.name)}" onchange="rset(${i},'name',this.value)">
      <button class="sm dan" onclick="delRule(${i})">🗑</button></div>
    <div class="grid2" style="margin-top:8px"><div><label>Ki korle (trigger)</label><select onchange="rtype(${i},this.value)">
      <option value="reaction" ${t.type==="reaction"?"selected":""}>Message e react</option>
      <option value="command" ${t.type==="command"?"selected":""}>Reply command</option></select></div><div>${trig}</div></div>
    <div class="grid2"><div><label>Ke korle kaj hobe</label><select onchange="rset(${i},'who',this.value)">
      <option value="me" ${r.who==="me"?"selected":""}>Shudhu ami</option><option value="trusted" ${r.who==="trusted"?"selected":""}>Ami + trusted</option></select></div>
      <div><label>&nbsp;</label><label class="chk"><input type="checkbox" ${r.confirm?"checked":""} onchange="rset(${i},'confirm',this.checked)"> Age confirm chao</label></div></div>
    <h3>Kon group e</h3><div>${scope}</div>
    <h3>Ki hobe (serial e)</h3>${r.actions.map((a,j)=>actHTML(a,i,j)).join("")}
    <div style="margin-top:8px"><button class="sm ghost" onclick="addAct(${i})">＋ Action</button></div></div>`;
}
function renderRules(){
  if(!R){ $("main").innerHTML = ""; return; }
  $("main").innerHTML = `<div class="card"><h2>⚡ Rules</h2>
    <div class="muted">Reaction e emoji ta group e allowed thakte hobe. Command: message e reply diye <b>${esc(S.settings.prefix)}ban</b> likho.</div></div>` +
    R.map(ruleHTML).join("") +
    `<div class="row"><button class="ghost" onclick="addRule()">＋ Notun rule</button><button class="pri" onclick="saveRules()">💾 Save rules</button></div>`;
}
async function saveRules(){
  const r = await api("api/rules_save", {rules:R});
  if(r.ok){ R = r.rules; toast("Rules save hoyeche ✅"); render(); } else toast(r.error, true);
}

/* ============================= people ============================= */
function renderPeople(){
  if(!TR){ $("main").innerHTML = ""; return; }
  const permOpts = ["*"].concat(S.action_types);
  let h = `<div class="card"><h2>👥 Trusted moderator</h2>
    <div class="muted">Eder react/command e rule kaj korbe (rule e "Ami + trusted" bachle) - shudhu tader dewa adhikar onujayi.</div>` +
    TR.map((t,i)=>`<div class="act"><div class="grid2"><div><label>User ID</label><input type="number" value="${t.id}" onchange="TR[${i}].id=+this.value"></div>
      <div><label>Nam (mone rakhar jonno)</label><input type="text" value="${esc(t.name||"")}" onchange="TR[${i}].name=this.value"></div></div>
      <div class="grid3">${permOpts.map(p=>`<label class="chk"><input type="checkbox" ${(t.perms||[]).includes(p)?"checked":""} onchange="tperm(${i},'${p}',this.checked)"> ${p==="*"?"Sob":(ACT_BN[p]||p)}</label>`).join("")}</div>
      <div style="margin-top:8px"><button class="sm dan" onclick="TR.splice(${i},1);render()">Remove</button></div></div>`).join("") +
    `<div class="row"><button class="ghost" onclick="TR.push({id:0,name:'',perms:['mute','warn','delete']});render()">＋ Trusted</button></div></div>`;
  const bl = S.blacklist||[];
  h += `<div class="card"><h2>🚫 Blacklist (${bl.length})</h2>
    <div class="muted">Blacklist e thakle tar SOB message auto delete hobe.</div>
    <div class="row" style="margin-top:8px"><input type="text" class="grow" id="bli" placeholder="User ID (reply ba id diye o kora jay)">
      <button class="sm pri" onclick="blAdd(+$('bli').value,'')">Add</button></div>` +
    (bl.length ? bl.map(b=>`<div class="hline"><div class="t"><b>${esc(b.name||b.id)}</b><span class="muted">${b.id} · ${b.reason||""} · ${fmtT(b.t)}</span></div>
      <button class="sm ghost" onclick="blDel(${b.id})">Tule nao</button></div>`).join("") : `<div class="muted" style="margin-top:8px">Khali</div>`) + `</div>`;
  const off = S.stats.offenders||[];
  if(off.length){
    h += `<div class="card"><h2>😈 Link offender</h2>` + off.map(o=>`<div class="hline"><div class="t"><b>${esc(o.name||o.id)}</b>
      <span class="muted">${o.n} bar · ${o.chat||""}</span></div>
      <button class="sm dan" onclick="blAdd(${o.id},'')">🚫 Blacklist</button></div>`).join("") + `</div>`;
  }
  h += `<div class="card"><h2>⛔ Global ban (sob group)</h2>` +
    ((S.gban||[]).length ? S.gban.map(g=>`<div class="hline"><div class="t"><b>${esc(g.name||g.id)}</b><span class="muted">${g.id}</span></div>
      <button class="sm ghost" onclick="ungban(${g.id})">Tule nao</button></div>`).join("") : `<div class="muted">Keu global ban e nai</div>`) + `</div>`;
  h += `<div class="card"><h2>🛡️ Surokkhito list</h2>
    <div class="muted">Admin ra ager theke surokkhito. Onno kauke rakhte chaile user ID ek line e ekta.</div>
    <textarea id="prot" style="margin-top:6px">${esc(PR)}</textarea>
    <div class="row" style="margin-top:10px"><button class="pri" onclick="savePeople()">💾 Save</button></div></div>`;
  $("main").innerHTML = h;
}
async function blDel(id){ const r = await api("api/blacklist",{id,remove:true}); toast(r.ok?"Tule neoa holo":r.error,!r.ok); refresh(true); }
async function ungban(id){ if(!ask("Sob group theke unban korbe?")) return; const r = await api("api/do",{user:id,action:{type:"ungban"}}); toast(r.msg||"Hoyeche",!r.ok); refresh(true); inited.people=false; }
function tperm(i,p,on){ const s=new Set(TR[i].perms||[]); on?s.add(p):s.delete(p); TR[i].perms=Array.from(s); }
async function savePeople(){
  PR = $("prot").value;
  const prot = PR.split("\n").map(s=>s.trim()).filter(Boolean).map(Number).filter(n=>n);
  const r = await api("api/lists_save", {trusted:TR.filter(t=>t.id), protected:prot});
  if(r.ok){ toast("Save hoyeche ✅"); refresh(true); } else toast("Save hoyni", true);
}

/* ============================= log ============================= */
function renderLog(){
  let h = `<div class="card"><h2>📜 Log</h2>
    <div class="row"><input type="text" class="grow" placeholder="🔍 Khujo…" value="${esc(logQ)}" oninput="logQ=this.value;render()">
    ${["all","action","error","dry"].map(k=>`<button class="sm ${logFilter===k?"pri":"ghost"}" onclick="logFilter='${k}';render()">${k}</button>`).join("")}
    <button class="sm ghost" onclick="refresh(true)">🔄</button></div></div><div class="card">`;
  let rows = S.logs||[];
  if(logFilter !== "all") rows = rows.filter(l => logFilter==="action" ? l.kind==="action" : l.kind===logFilter);
  if(logQ) rows = rows.filter(l => JSON.stringify(l).toLowerCase().includes(logQ.toLowerCase()));
  h += rows.length ? rows.map(logRow).join("") : `<div class="muted">Kichu nai</div>`;
  $("main").innerHTML = h + `</div>`;
}

/* ============================= settings ============================= */
function renderSettings(){
  if(!ST){ $("main").innerHTML = ""; return; }
  const c = (k,n) => `<label class="sw"><input type="checkbox" id="s_${k}" ${ST[k]?"checked":""}><span class="tk"></span>${n}</label>`;
  const nb = (k,n) => `<div><label>${n}</label><input type="number" id="s_${k}" min="0" value="${ST[k]}"></div>`;
  $("main").innerHTML = `
  <div class="card"><h2>🔐 Nirapotta</h2>
    ${c("dry_run","Dry-run (kono kaj hobe na, shudhu log - test er jonno)")}
    ${c("confirm_all","Sob action e age confirm chao")}
    <div class="grid2">${nb("undo_seconds","React diye koto sec er moddhe sariye nile bondho (0=off)")}${nb("max_actions_per_min","Minite sorboccho action")}</div>
    ${nb("react_max_age_h","Koto ghonta purano message e react e kaj hobe na (0=off)")}</div>
  <div class="card"><h2>🛡️ Link Shield (sob group er jonno)</h2>
    ${c("link_guard","Master switch (bondho dile kothao link delete hobe na)")}
    ${c("link_all_admin_groups","Notun group e apna apni chalu")}
    ${c("link_notice","Group e warning dekhaw")}
    ${c("link_block_edit","Edit kore link bosaleo dhoro")}
    ${c("link_block_buttons","Inline URL button wala message delete")}
    ${c("link_bot_fallback","Main account fail korle bot diye delete")}
    ${c("auto_blacklist","Bar bar link dile auto blacklist")}
    <div class="grid2">${nb("link_notice_s","Warning koto sec pore muchbe")}${nb("auto_blacklist_after","Koybar link dile blacklist")}</div></div>
  <div class="card"><h2>⌨️ Command</h2><div class="grid2">
    <div><label>Command prefix</label><input type="text" id="s_prefix" value="${esc(ST.prefix)}"></div>
    ${nb("reply_delete_s","Command er uttor koto sec pore muchbe (0=na)")}</div>
    ${c("delete_command","Command dewar por oi message muche daw")}
    <div class="muted">Commands: .ban .mute .kick .warn .del .purge .lock .unlock .gban .shield .bl .stats .id .linktest .wl</div></div>
  <div class="card"><h2>⚠️ Warn</h2><div class="grid2">${nb("warn_limit","Koyta warn e shasti")}
    <div><label>Shasti</label><select id="s_warn_action">
      <option value="mute" ${ST.warn_action==="mute"?"selected":""}>Mute</option>
      <option value="ban" ${ST.warn_action==="ban"?"selected":""}>Ban</option>
      <option value="kick" ${ST.warn_action==="kick"?"selected":""}>Kick</option></select></div></div>
    ${nb("warn_mute_min","Mute hole koto minit")}${c("notify_in_chat","Warn dile group e jaanao")}</div>
  <div class="card"><h2>📣 Aro</h2>${c("cas_check","Notun member ke CAS spam list e dekho")}
    ${c("delete_join_left","Join/Leave message sob group e muchhe felo")}
    <label>Log group/channel (sob action er khobor)</label><input type="text" id="s_log_chat" value="${esc(ST.log_chat||"")}" placeholder="@mylogs ba -100..."></div>
  <div class="card"><h2>📢 Broadcast</h2>
    <div class="muted">Ei message ta tomar sob admin group e jabe.</div>
    <textarea id="bc" placeholder="Sob group e ja pathate chao…" style="margin-top:8px"></textarea>
    <div class="row" style="margin-top:8px"><button class="pri" onclick="broadcast()">📢 Sob group e pathao</button></div></div>
  <div class="card"><h2>🤖 Bot (confirm + captcha er jonno)</h2>
    <label>Bot token (@BotFather theke)</label><input type="text" id="s_bot_token" value="${esc(ST.bot_token)}" placeholder="123456:ABC…">
    <div class="muted" style="margin-top:6px">Bot ke ekbar /start dao, ar captcha chaile group e admin koro.</div></div>
  <div class="card"><h2>💾 Backup</h2><div class="row">
    <button class="ghost" onclick="exportCfg()">⬇ Download</button>
    <button class="ghost" onclick="$('impf').click()">⬆ Restore</button>
    <input type="file" id="impf" accept=".json" class="hide" onchange="importCfg(this)"></div></div>
  <div class="row"><button class="pri" onclick="saveSettings()">💾 Save settings</button></div>`;
}
async function saveSettings(){
  const o = {}, g = k => $("s_"+k);
  for(const k of ["dry_run","confirm_all","delete_command","notify_in_chat","cas_check","link_guard","link_all_admin_groups",
      "link_notice","link_block_edit","link_block_buttons","link_bot_fallback","auto_blacklist","delete_join_left"])
    if(g(k)) o[k] = g(k).checked;
  for(const k of ["undo_seconds","max_actions_per_min","react_max_age_h","warn_limit","warn_mute_min","link_notice_s",
      "auto_blacklist_after","reply_delete_s"])
    if(g(k)) o[k] = +g(k).value || 0;
  if(g("prefix")) o.prefix = g("prefix").value || ".";
  if(g("log_chat")) o.log_chat = g("log_chat").value;
  if(g("warn_action")) o.warn_action = g("warn_action").value;
  if(g("bot_token")) o.bot_token = g("bot_token").value;
  const r = await api("api/settings_save", {settings:o});
  if(r.ok){ toast("Save hoyeche ✅" + (r.bot?" · bot "+r.bot:"")); inited.settings = false; refresh(true); } else toast("Save hoyni", true);
}
async function broadcast(){
  const t = $("bc").value.trim(); if(!t) return toast("Ki pathabe likho", true);
  if(!ask("Sob admin group e pathabo - thik ache?")) return;
  const r = await api("api/broadcast", {text:t});
  toast(r.ok ? `${r.sent} ta group e pathano holo` : (r.error||"Hoyni"), !r.ok);
}
async function exportCfg(){
  const r = await api("api/export"); const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(r.data,null,1)],{type:"application/json"}));
  a.download = "moderator-backup.json"; a.click();
}
async function importCfg(inp){
  const f = inp.files[0]; if(!f) return;
  try{ const d = JSON.parse(await f.text()); const r = await api("api/import",{data:d});
    toast(r.ok?"Restore hoyeche ✅":r.error, !r.ok);
    inited = {rules:false,people:false,settings:false,shield:false}; G=null; refresh(true);
  }catch(e){ toast("File thik na", true); }
  inp.value = "";
}

/* ============================= main ============================= */
function render(){
  if(!S) return;
  badge();
  if(tab === "dashboard") renderDashboard();
  else if(tab === "groups") renderGroups();
  else if(tab === "shield") renderShield();
  else if(tab === "rules") renderRules();
  else if(tab === "people") renderPeople();
  else if(tab === "log") renderLog();
  else if(tab === "settings") renderSettings();
}
async function refresh(force){
  try{
    S = await api("api/state");
    if(!inited.rules){ R = JSON.parse(JSON.stringify(S.rules)); inited.rules = true; }
    if(!inited.people){ TR = JSON.parse(JSON.stringify(S.trusted)); PR = S.protected.join("\n"); inited.people = true; }
    if(!inited.settings){ ST = JSON.parse(JSON.stringify(S.settings)); inited.settings = true; }
    const typing = document.activeElement && ["TEXTAREA","INPUT","SELECT"].includes(document.activeElement.tagName);
    // form er kaj nosto na hobe - tai sudhu Dashboard/Log auto refresh hobe
    if(force || (!typing && (tab === "dashboard" || tab === "log"))) render();
    else badge();
  }catch(e){
    $("badge").textContent = "offline"; $("badge").className = "badge b-need_session";
  }
}
renderNav(); refresh(true);
setInterval(() => { const t = document.activeElement; if(!t || !["TEXTAREA","INPUT","SELECT","BUTTON"].includes(t.tagName)) refresh(false); }, 5000);
</script>
</body>
</html>
"""
