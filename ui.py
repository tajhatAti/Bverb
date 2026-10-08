"""ui.py - website er HTML (ekta file e)"""
HTML = r"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Group Moderator</title>
<style>
  :root{--bg:#10131a;--panel:#181d27;--line:#262d3b;--text:#e8ebf2;--muted:#8a94a8;--ok:#4ade80;--warn:#fbbf24;--err:#f87171;--info:#7dd3fc}
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--bg);color:var(--text);font-family:"Segoe UI",system-ui,"Noto Sans Bengali",sans-serif;padding:14px;max-width:820px;margin:0 auto;line-height:1.45}
  h1{font-size:19px;margin:2px 0}
  h2{font-size:15px;margin:18px 0 8px}
  h3{font-size:13px;margin:12px 0 6px;color:var(--muted);font-weight:600}
  .muted{color:var(--muted);font-size:12.5px}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;margin-bottom:10px}
  .badge{display:inline-block;padding:2px 10px;border-radius:99px;font-size:12px;font-weight:600}
  .b-ready{background:#0d3d2a;color:var(--ok)} .b-need_session{background:#1d3550;color:var(--info)}
  .b-connecting{background:#3a3515;color:var(--warn)}
  input[type=text],input[type=number],select,textarea{width:100%;background:#0c0f15;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px;font-size:14px}
  textarea{min-height:90px;font-family:ui-monospace,Consolas,monospace;font-size:12px;resize:vertical}
  input:focus,select:focus,textarea:focus,button:focus-visible{outline:2px solid var(--info);outline-offset:1px}
  label{display:block;font-size:12px;color:var(--muted);margin:8px 0 3px}
  label.chk{display:inline-flex;align-items:center;gap:6px;margin:6px 12px 0 0;color:var(--text);font-size:13px}
  button{background:var(--info);color:#06202e;border:0;border-radius:8px;padding:8px 14px;font-size:13.5px;font-weight:700;cursor:pointer}
  button:disabled{opacity:.5}
  button.sec{background:#2a3244;color:var(--text)} button.red{background:#5a2222;color:#ffd0d0}
  button.sm{padding:5px 9px;font-size:12px} button.ghost{background:transparent;color:var(--muted);border:1px solid var(--line);font-weight:500}
  .row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  .grow{flex:1;min-width:120px}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:8px}
  .tabs{display:flex;gap:6px;overflow-x:auto;margin:10px 0;padding-bottom:4px}
  .tabs button{background:#232a38;color:var(--muted);white-space:nowrap}
  .tabs button.on{background:var(--info);color:#06202e}
  .hide{display:none !important}
  .chip{display:inline-block;background:#232a38;border-radius:99px;padding:1px 9px;font-size:11.5px;margin:2px 4px 0 0;color:var(--muted)}
  .chip.g{color:var(--ok)} .chip.r{color:var(--err)}
  .log{border-left:3px solid var(--line);padding:6px 10px;margin-bottom:6px;background:var(--panel);border-radius:0 8px 8px 0;font-size:13px}
  .log.action{border-color:var(--ok)} .log.error{border-color:var(--err)} .log.cancel,.log.dry,.log.limit{border-color:var(--warn)}
  .log.bad{border-color:var(--err)}
  .act{background:#12161e;border:1px solid var(--line);border-radius:8px;padding:8px;margin-top:8px}
  .msg{font-size:13px;min-height:18px;margin-top:6px} .msg.g{color:var(--ok)} .msg.e{color:var(--err)}
  details.sec{border:1px solid var(--line);border-radius:8px;margin-top:8px;background:#12161e}
  details.sec>summary{cursor:pointer;padding:9px 10px;font-size:13.5px;font-weight:600;list-style:none}
  details.sec>summary::-webkit-details-marker{display:none}
  details.sec>summary:after{content:"+";float:right;color:var(--muted)}
  details.sec[open]>summary:after{content:"-"}
  details.sec>div{padding:0 10px 10px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 8px}
  #toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:#232a38;border:1px solid var(--line);padding:9px 16px;border-radius:10px;font-size:13px;z-index:9;max-width:90%}
</style>
</head>
<body>

<div class="row" style="justify-content:space-between">
  <div><h1>Group Moderator</h1><div class="muted" id="who">-</div></div>
  <span id="badge" class="badge b-need_session">...</span>
</div>

<div class="tabs" id="tabs"></div>

<div id="tab_status"></div>
<div id="tab_groups" class="hide"></div>
<div id="tab_rules" class="hide"></div>
<div id="tab_people" class="hide"></div>
<div id="tab_log" class="hide"></div>
<div id="tab_settings" class="hide"></div>
<div id="toast" class="hide"></div>

<script>
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtT = t => new Date(t*1000).toLocaleString();
const TABS = [["status","Status"],["groups","Groups"],["rules","Rules"],["people","People"],["log","Log"],["settings","Settings"]];
const ACT_BN = {ban:"Ban",mute:"Mute",unban:"Unban",unmute:"Unmute",kick:"Kick",warn:"Warn",unwarn:"Unwarn",
  delete:"Message delete",delete_all:"Sob message delete",promote:"Admin banao",demote:"Admin theke namao",
  add_to_group:"Onno group e add",dm:"DM pathao",reply:"Group e reply",pin:"Pin",unpin:"Unpin",
  restrict:"Restrict (shudhu dekhte parbe)",lock:"Group lock",unlock:"Group unlock",slowmode:"Slowmode",
  purge:"Message purge",gban:"Sob group e ban",ungban:"Sob group theke unban"};
const PERMS = [["send_messages","Message dite parbe"],["send_media","Media"],["send_stickers","Sticker"],["send_gifs","GIF"],
  ["send_polls","Poll"],["embed_link_previews","Link preview"],["invite_users","Invite"],["pin_messages","Pin"],["change_info","Group info"]];
const LOCKS = [["links","Link"],["mention","@mention"],["hashtag","#hashtag"],["email","Email"],["phone","Phone no."],
  ["long","Lomba message"],["emoji","Onek emoji"],["inline_buttons","Inline button"],["via_bot","Inline bot"],["forward","Forward"],
  ["photo","Chhobi"],["video","Video"],["sticker","Sticker"],["gif","GIF"],["voice","Voice"],["video_note","Gol video"],
  ["audio","Audio"],["document","File"],["poll","Poll"],["contact","Contact"],["location","Location"],["game","Game"]];
const LOCK_NAMES = LOCKS.map(x => x[0]);
const RIGHTS = [["delete_messages","Message delete"],["ban_users","Ban/Mute"],["invite_users","Invite"],["pin_messages","Pin"],
  ["change_info","Group info"],["add_admins","Admin banano"],["manage_call","Voice chat"],["anonymous","Anonymous"]];

let S = null, G = null, R = null, TR = null, PR = "", ST = null;
let tab = "status", inited = {rules:false, people:false, settings:false}, openG = {}, busy = false;

async function api(path, body){
  const r = body === undefined ? await fetch(path) : await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  return r.json();
}
function toast(t, bad){
  const el = $("toast"); el.textContent = t; el.style.color = bad ? "var(--err)" : "var(--text)"; el.classList.remove("hide");
  clearTimeout(toast.t); toast.t = setTimeout(()=>el.classList.add("hide"), 3500);
}
function showTab(t){
  tab = t;
  for(const [k] of TABS) $("tab_"+k).classList.toggle("hide", k !== t);
  renderTabs();
  if(t === "groups" && !G) loadGroups();
  if(t === "rules" && !G) loadGroups(true);
  render();
}
function renderTabs(){
  $("tabs").innerHTML = TABS.map(([k,n]) => `<button class="${k===tab?"on":""}" onclick="showTab('${k}')">${n}</button>`).join("");
}

/* ---------------- status ---------------- */
function renderStatus(){
  const b = $("badge"); b.textContent = S.status.replace("_"," "); b.className = "badge b-" + S.status;
  $("who").textContent = S.me ? S.me + (S.bot ? "  ·  bot " + S.bot : "") : "Session connect hoyni";
  let h = "";
  if(S.status !== "ready"){
    h += `<div class="panel"><h3>Main session string paste koro</h3>
      <textarea id="sess" placeholder="1BVts..." spellcheck="false"></textarea>
      <div class="row" style="margin-top:8px"><button id="cbtn" onclick="connect()">Connect</button></div>
      <div class="msg e" id="cerr">${esc(S.error)}</div></div>`;
  } else {
    h += `<div class="panel"><div class="row" style="justify-content:space-between">
      <div><b>${esc(S.me)}</b><div class="muted">Bot: ${esc(S.bot || "nai (Settings e token dile confirm/captcha bortone pabe)")}<br>
      Speed boost (cryptg): <span style="color:var(${S.cryptg?"--ok":"--err"})">${S.cryptg?"ON":"OFF"}</span></div></div>
      <button class="ghost sm" onclick="logout()">Logout</button></div></div>`;
  }
  if(S.pending.length){
    h += `<h2>Confirm lagbe</h2>` + S.pending.map(p => `<div class="panel"><div>${esc(p.summary)}</div>
      <div class="row" style="margin-top:8px"><button class="sm" onclick="confirmIt('${p.id}',true)">✅ Hobe</button>
      <button class="sm red" onclick="confirmIt('${p.id}',false)">❌ Na</button></div></div>`).join("");
  }
  h += `<h2>React test (Telegram update pathacche kina)</h2>
    <div class="muted" style="margin-bottom:6px">Kono group e kono message e react dao. Niche row ashle bujhbe Telegram tomake react er khobor pathacche. Row na ashle react-trigger kaj korbe na, tokhon reply-command (.ban) bebohar koro.</div>`;
  h += S.react_debug.length ? S.react_debug.map(d => `<div class="log"><span class="muted">${fmtT(d.t)}</span> · msg ${d.msg}<br>
     Ami dilam: ${d.mine.length ? esc(d.mine.join(" ")) : "kichu na"} ${d.min ? '<span class="chip">min update</span>' : ""}<br><span class="muted">${esc(d.note)}</span></div>`).join("")
    : '<div class="muted">Ekhono kono react update ashe ni</div>';
  const keepSess = $("sess") ? $("sess").value : "";
  $("tab_status").innerHTML = h;
  if($("sess")) $("sess").value = keepSess;
}
async function connect(){
  const s = $("sess").value.trim(); if(!s) return;
  $("cbtn").disabled = true; $("cbtn").textContent = "Connecting...";
  const r = await api("api/connect", {session:s});
  if(!r.ok) toast(r.error || "Connect hoyni", true);
  await refresh(true); G = null;
}
async function logout(){ if(!confirm("Logout korbe?")) return; await api("api/logout", {}); G = null; await refresh(true); }
async function confirmIt(id, ok){ await api("api/confirm", {id, ok}); refresh(true); }

/* ---------------- groups ---------------- */
async function loadGroups(force){
  const r = await api("api/groups" + (force ? "?force=1" : ""));
  if(!r.ok){ toast(r.error || "Group list ashe ni", true); return; }
  G = r.groups; render();
}
function chipsFor(g){
  const x = g.rights, c = [];
  c.push(g.creator ? '<span class="chip g">Owner</span>' : g.admin ? '<span class="chip g">Admin</span>' : '<span class="chip r">Admin na</span>');
  for(const [k,n] of [["ban_users","Ban"],["delete_messages","Delete"],["add_admins","Admin banano"],["invite_users","Invite"],["pin_messages","Pin"]])
    if(g.admin) c.push(`<span class="chip ${x[k]?"g":"r"}">${n}</span>`);
  return c.join("");
}
function renderGroups(){
  if(!G){ $("tab_groups").innerHTML = '<div class="muted">Load hocche... (age session connect koro)</div>'; return; }
  let h = `<div class="row" style="margin-bottom:8px"><button class="sm sec" onclick="loadGroups(true)">Refresh</button>
    <span class="muted">${G.length} ta group</span></div>`;
  for(const g of G){
    const o = openG[g.id] || "";
    h += `<div class="panel" id="g_${g.id}">
      <div class="row" style="justify-content:space-between"><b>${esc(g.title)}</b>
        <label class="chk" style="margin:0"><input type="checkbox" ${g.cfg.enabled?"checked":""} onchange="gToggle(${g.id},this.checked)"> Chalu</label></div>
      <div>${chipsFor(g)}<span class="chip">${g.members||"?"} member</span></div>
      <div class="row" style="margin-top:8px">
        <button class="sm sec" onclick="gOpen(${g.id},'set')">Settings</button>
        <button class="sm sec" onclick="gOpen(${g.id},'mem')">Members</button>
        <button class="sm ghost" onclick="doAct(${g.id},0,{type:'lock',perms:{}})">Lock</button>
        <button class="sm ghost" onclick="doAct(${g.id},0,{type:'unlock'})">Unlock</button></div>
      <div id="gx_${g.id}">${o==="set" ? gForm(g) : o==="mem" ? gMembers(g) : ""}</div></div>`;
  }
  $("tab_groups").innerHTML = h;
  for(const g of G) if(openG[g.id] === "mem") memLoad(g.id);
}
function gOpen(id, what){ openG[id] = openG[id] === what ? "" : what; renderGroups(); }
async function gToggle(id, on){
  const g = G.find(x => x.id === id); g.cfg.enabled = on;
  const r = await api("api/group_save", {chat:id, cfg:g.cfg}); toast(r.ok ? "Save hoyeche" : r.error, !r.ok);
}
function gv(g, path){ return path.split(".").reduce((o,k) => o == null ? undefined : o[k], g.cfg); }
const fb = (g,p,l) => `<label class="chk"><input type="checkbox" data-g="${g.id}" data-p="${p}" data-t="b" ${gv(g,p)?"checked":""}> ${l}</label>`;
const fn = (g,p,l) => `<div><label>${l}</label><input type="number" data-g="${g.id}" data-p="${p}" data-t="n" value="${gv(g,p)}"></div>`;
const ft = (g,p,l) => `<div><label>${l}</label><input type="text" data-g="${g.id}" data-p="${p}" data-t="t" value="${esc(gv(g,p))}"></div>`;
const fa = (g,p,l,t,val) => `<label>${l}</label><textarea style="min-height:60px" data-g="${g.id}" data-p="${p}" data-t="${t}">${esc(val)}</textarea>`;
const fs = (g,p,l,opts,t) => `<div><label>${l}</label><select data-g="${g.id}" data-p="${p}" data-t="${t||"s"}">` +
  opts.map(([v,n]) => `<option value="${v}" ${String(v)===String(gv(g,p))?"selected":""}>${n}</option>`).join("") + `</select></div>`;
const sec = (t, inner) => `<details class="sec"><summary>${t}</summary><div>${inner}</div></details>`;
const ACT4 = [["strike","Dhap dhap (warn → mute)"],["delete","Shudhu muche felo"],["mute","Mute"],["ban","Ban"]];
function gForm(g){
  const c = g.cfg, am = c.automod, lk = am.locks;
  const lockSel = `<div><label>Lock bhangle ki hobe</label><select data-g="${g.id}" data-t="lockact">` +
    ACT4.map(([v,n]) => `<option value="${v}" ${lk.links.action===v?"selected":""}>${n}</option>`).join("") + `</select></div>`;
  const locks = `${fb(g,"automod.enabled","<b>Chalu</b>")}<h3>Ki ki dewa jabe na (tick = block)</h3><div class="grid2">` +
    LOCKS.map(([k,n]) => fb(g,`automod.locks.${k}.on`,n)).join("") + `</div>${lockSel}
    ${fa(g,"automod.links_allow","Ei link thakle block hobe na (ek line e ekta)","l",am.links_allow.join("\n"))}
    <div class="two">${fn(g,"automod.long_max","Lomba = koto akkhor+")}${fn(g,"automod.emoji_max","Onek emoji = koyta+")}</div>`;
  const st = am.strikes;
  const strikes = `<div class="muted">Prothom bar = shudhu hushiyar, tarpor mute (group e thakbe). Ek line e ekta: warn / mute 60 / kick / ban</div>
    ${fa(g,"automod.strikes.steps","Dhap gulo","steps",st.steps.map(s => s.action + (s.mute_min ? " " + s.mute_min : "")).join("\n"))}
    <div class="two">${fn(g,"automod.strikes.window_h","Koto ghonta er dhap gona hobe")}${fn(g,"automod.strikes.notify_delete_s","Hushiyar message koto sec pore muchbe")}</div>
    ${ft(g,"automod.strikes.warn_text","Hushiyar message ({name} {kind} {n} {max})")}`;
  const wf = `${fb(g,"automod.words.on","Nishiddho shobdo")}
    ${fa(g,"automod.words.list","Shobdo (ek line e ekta, regex hole re: diye shuru)","l",am.words.list.join("\n"))}
    ${fs(g,"automod.words.action","Shobdo e shasti",ACT4)}
    ${fb(g,"automod.flood.on","Flood (onek druto message)")}
    <div class="two">${fn(g,"automod.flood.count","Koyta message")}${fn(g,"automod.flood.seconds","Koto sec e")}</div>
    ${fn(g,"automod.flood.mute_min","Mute koto minit")}`;
  const join = `${fb(g,"antibot.on","Bot dhokano bondho")}
    <div class="two">${fs(g,"antibot.mode","Kake atkabe",[["non_admin","Admin na hole"],["everyone","Sobaike"]])}
    ${fs(g,"antibot.punish","Je add korlo tar shasti",[["none","Kichu na"],["warn","Dhap dhap"],["mute","Mute"],["ban","Ban"]])}</div>
    ${fb(g,"antiraid.on","Anti-raid (onek jon ekshathe dhukle group lock)")}
    <div class="two">${fn(g,"antiraid.joins","Koyjon")}${fn(g,"antiraid.seconds","Koto sec e")}</div>${fn(g,"antiraid.lock_min","Lock koto minit")}
    ${fb(g,"automod.newbie.on","Notun member der link/media block")}
    <div class="two">${fn(g,"automod.newbie.hours","Koto ghonta")}${fs(g,"automod.newbie.block","Ki block",[["links,media","Link + media"],["links","Shudhu link"],["media","Shudhu media"]],"csv")}</div>`;
  const night = `${fb(g,"night.on","Night mode (rate e group lock)")}
    <div class="two">${ft(g,"night.from","Shuru (HH:MM)")}${ft(g,"night.to","Shesh (HH:MM)")}</div>${fn(g,"night.tz","Timezone minit (Bangladesh = 360)")}
    <h3>Service message muche felo</h3>${fb(g,"clean.join","Join")}${fb(g,"clean.leave","Leave")}${fb(g,"clean.pin","Pin")}`;
  const wel = `${fb(g,"welcome.on","Welcome message")}${ft(g,"welcome.text","Text ({name} {group})")}${fn(g,"welcome.delete_after","Koto sec pore muchbe (0 = na)")}
    ${fb(g,"captcha.on","Captcha (bot lagbe)")}${ft(g,"captcha.text","Captcha text")}
    <div class="two">${fn(g,"captcha.timeout_min","Koto minit somoy")}${fs(g,"captcha.fail","Fail hole",[["kick","Kick"],["ban","Ban"]])}</div>`;
  const rules = `${fa(g,"rules_text",".rules likhle ja dekhabe","ta",c.rules_text||"")}
    ${fa(g,"filters","Auto reply: ek line e  shobdo => reply","filters",(c.filters||[]).map(f => f.key + " => " + f.reply).join("\n"))}`;
  return sec("Lock (link, media, button...)", locks) + sec("Shasti (dhap dhap)", strikes) + sec("Shobdo ar flood", wf) +
    sec("Notun member, bot, raid", join) + sec("Night mode ar safai", night) + sec("Welcome ar captcha", wel) +
    sec("Rules ar auto reply", rules) +
    `<div class="row" style="margin-top:12px"><button onclick="gSave(${g.id})">Save</button></div>`;
}
function setP(o, path, v){
  const ks = path.split(".");
  for(let i = 0; i < ks.length - 1; i++) o = o[ks[i]] = o[ks[i]] || {};
  o[ks[ks.length-1]] = v;
}
async function gSave(id){
  const g = G.find(x => x.id === id), cfg = {enabled: g.cfg.enabled}; let lockact = "strike";
  document.querySelectorAll(`[data-g="${id}"]`).forEach(el => {
    const t = el.dataset.t, p = el.dataset.p; let v;
    if(t === "lockact"){ lockact = el.value; return; }
    if(t === "b") v = el.checked;
    else if(t === "n") v = parseFloat(el.value) || 0;
    else if(t === "l") v = el.value.split("\n").map(s => s.trim()).filter(Boolean);
    else if(t === "steps") v = el.value.split("\n").map(s => s.trim()).filter(Boolean).map(l => { const a = l.split(/\s+/); return {action:a[0].toLowerCase(), mute_min:parseInt(a[1]) || 0}; });
    else if(t === "filters") v = el.value.split("\n").map(s => s.trim()).filter(Boolean).map(l => { const i = l.indexOf("=>"); return i < 0 ? null : {key:l.slice(0,i).trim(), reply:l.slice(i+2).trim()}; }).filter(Boolean);
    else if(t === "csv") v = el.value.split(",").filter(Boolean);
    else v = el.value;
    setP(cfg, p, v);
  });
  cfg.automod = cfg.automod || {}; cfg.automod.locks = cfg.automod.locks || {};
  for(const n of LOCK_NAMES){ cfg.automod.locks[n] = cfg.automod.locks[n] || {}; cfg.automod.locks[n].action = lockact; }
  const r = await api("api/group_save", {chat:id, cfg});
  if(r.ok){ g.cfg = r.cfg; toast("Save hoyeche"); } else toast(r.error, true);
}
function gMembers(g){
  return `<h3>Members</h3><div class="row"><input type="text" class="grow" id="mq_${g.id}" placeholder="Nam ba @username khujo">
    <button class="sm" onclick="memLoad(${g.id})">Khujo</button></div><div id="ml_${g.id}" class="muted" style="margin-top:8px">Load hocche...</div>`;
}
async function memLoad(id){
  const q = ($("mq_"+id) || {}).value || "";
  const r = await api(`api/members?chat=${id}&q=${encodeURIComponent(q)}`);
  const el = $("ml_"+id); if(!el) return;
  if(!r.ok){ el.textContent = r.error; return; }
  el.innerHTML = r.members.length ? r.members.map(m => `<div class="panel" style="margin:6px 0">
    <div><b>${esc(m.name)}</b> ${m.username ? '<span class="muted">@'+esc(m.username)+'</span>' : ""}
      ${m.admin ? '<span class="chip g">Admin</span>' : ""}${m.bot ? '<span class="chip">Bot</span>' : ""}${m.warns ? `<span class="chip r">${m.warns} warn</span>` : ""}</div>
    <div class="row" style="margin-top:6px">
      <button class="sm red" onclick="doAct(${id},${m.id},{type:'mute',duration_min:60})">Mute 1h</button>
      <button class="sm red" onclick="doAct(${id},${m.id},{type:'ban'})">Ban</button>
      <button class="sm sec" onclick="doAct(${id},${m.id},{type:'warn'})">Warn</button>
      <select style="width:auto" onchange="moreAct(${id},${m.id},this)"><option value="">Aro...</option>
        <option value="kick">Kick</option><option value="restrict">Read-only 1h</option><option value="promote">Admin banao</option>
        <option value="demote">Admin theke namao</option><option value="unban">Unban / Unmute</option><option value="gban">Sob group e ban</option></select></div></div>`).join("")
    : "Kono member paoa jayni";
}
function moreAct(chat, user, sel){
  const v = sel.value; sel.value = ""; if(!v) return;
  const a = {kick:{type:"kick"}, restrict:{type:"restrict",duration_min:60,perms:{}},
    promote:{type:"promote",title:"Moderator",rights:{delete_messages:true,ban_users:true,invite_users:true,pin_messages:true}},
    demote:{type:"demote"}, unban:{type:"unban"}, gban:{type:"gban"}}[v];
  doAct(chat, user, a);
}
async function doAct(chat, user, action){
  if(["ban","kick","mute","gban","restrict","lock","purge"].includes(action.type) && !confirm(ACT_BN[action.type] + " korbe?")) return;
  const r = await api("api/do", {chat, user, action}); toast(r.msg || (r.ok ? "Hoyeche" : "Hoyni"), !r.ok);
  refresh(true);
}

/* ---------------- rules ---------------- */
function rset(i, path, val){
  const ks = path.split("."); let o = R[i];
  for(let k = 0; k < ks.length - 1; k++){ o[ks[k]] = o[ks[k]] || {}; o = o[ks[k]]; }
  o[ks[ks.length-1]] = val;
}
function aset(i, j, key, val){ R[i].actions[j][key] = val; }
function apset(i, j, key, val){ const a = R[i].actions[j]; a.perms = a.perms || {}; a.perms[key] = val; }
function arset(i, j, key, val){ const a = R[i].actions[j]; a.rights = a.rights || {}; a.rights[key] = val; }
function rtype(i, v){ R[i].trigger = v === "reaction" ? {type:"reaction", emoji:"🤬"} : {type:"command", name:"cmd"}; renderRules(); }
function atype(i, j, v){
  const a = {type:v};
  if(v === "ban") Object.assign(a, {duration_min:0, delete_history:false});
  if(v === "mute") a.duration_min = 60;
  if(v === "promote") Object.assign(a, {title:"", rights:{delete_messages:true,ban_users:true,invite_users:true,pin_messages:true}});
  if(v === "add_to_group") Object.assign(a, {target_group:"", text:"Ei group e join koro: {link}"});
  if(v === "dm") a.text = "Hi {name}";
  if(v === "reply") Object.assign(a, {text:"OK", delete_after:0});
  if(v === "restrict") Object.assign(a, {duration_min:60, perms:{}});
  if(v === "lock") Object.assign(a, {duration_min:0, perms:{}});
  if(v === "slowmode") a.seconds = 30;
  R[i].actions[j] = a; renderRules();
}
function addAct(i){ R[i].actions.push({type:"delete"}); renderRules(); }
function delAct(i, j){ R[i].actions.splice(j,1); renderRules(); }
function addRule(){ R.push({id:"r_"+Date.now(), name:"Notun rule", enabled:true, trigger:{type:"reaction", emoji:"🤬"}, who:"me", groups:["*"], confirm:false, actions:[{type:"delete"}]}); renderRules(); }
function delRule(i){ if(!confirm("Rule ta muche felbe?")) return; R.splice(i,1); renderRules(); }
function gscope(i, id, on){
  let gs = R[i].groups.filter(x => x !== "*"); id = String(id);
  gs = gs.filter(x => x !== id); if(on) gs.push(id); R[i].groups = gs;
}
function allScope(i, on){ R[i].groups = on ? ["*"] : []; renderRules(); }
function actHTML(a, i, j){
  let p = "";
  if(a.type === "ban") p = `<label>Koto minit (0 = chirokal)</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)">
    <label class="chk"><input type="checkbox" ${a.delete_history?"checked":""} onchange="aset(${i},${j},'delete_history',this.checked)"> Oi user er sob message muchbe</label>`;
  else if(a.type === "mute") p = `<label>Koto minit (0 = jotokkhon na unmute kori)</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)">`;
  else if(a.type === "promote") p = `<label>Custom title (max 16 akkhor, {name} cholbe)</label><input type="text" value="${esc(a.title||"")}" onchange="aset(${i},${j},'title',this.value)">` +
    `<div>` + RIGHTS.map(([k,n]) => `<label class="chk"><input type="checkbox" ${(a.rights||{})[k]?"checked":""} onchange="arset(${i},${j},'${k}',this.checked)"> ${n}</label>`).join("") + `</div>`;
  else if(a.type === "add_to_group") p = `<label>Kon group e add korbe</label><select onchange="aset(${i},${j},'target_group',this.value)"><option value="">-- bachho --</option>` +
    (G||[]).map(g => `<option value="${g.id}" ${String(a.target_group)===String(g.id)?"selected":""}>${esc(g.title)}</option>`).join("") + `</select>
    <label>Privacy te add na holey DM e ja pathabe ({link})</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">`;
  else if(a.type === "restrict" || a.type === "lock") p = `<label>Koto minit (0 = ${a.type==="lock"?"jotokkhon na unlock kori":"chirokal"})</label><input type="number" min="0" value="${a.duration_min||0}" onchange="aset(${i},${j},'duration_min',+this.value)">
    <div class="muted" style="margin-top:6px">Ki ki korte parbe (kichu tick na dile = shudhu dekhte parbe)</div><div>` +
    PERMS.filter(x => a.type === "restrict" || !["invite_users","pin_messages","change_info"].includes(x[0])).map(([k,n]) => `<label class="chk"><input type="checkbox" ${(a.perms||{})[k]?"checked":""} onchange="apset(${i},${j},'${k}',this.checked)"> ${n}</label>`).join("") + `</div>`;
  else if(a.type === "slowmode") p = `<label>Second</label><select onchange="aset(${i},${j},'seconds',+this.value)">` + [0,10,30,60,300,900,3600].map(v => `<option value="${v}" ${a.seconds===v?"selected":""}>${v ? v + " sec" : "bondho"}</option>`).join("") + `</select>`;
  else if(a.type === "reply") p = `<label>Text ({name} {group} cholbe)</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">
    <label>Koto sec pore muchbe (0 = na)</label><input type="number" min="0" value="${a.delete_after||0}" onchange="aset(${i},${j},'delete_after',+this.value)">`;
  else if(a.type === "dm") p = `<label>Text ({name} {group} cholbe)</label><input type="text" value="${esc(a.text||"")}" onchange="aset(${i},${j},'text',this.value)">`;
  return `<div class="act"><div class="row"><select class="grow" onchange="atype(${i},${j},this.value)">` +
    S.action_types.map(t => `<option value="${t}" ${t===a.type?"selected":""}>${ACT_BN[t]||t}</option>`).join("") +
    `</select><button class="sm red" onclick="delAct(${i},${j})">✕</button></div>${p}</div>`;
}
function ruleHTML(r, i){
  const t = r.trigger || {}, all = (r.groups||[]).includes("*");
  const trig = t.type === "reaction"
    ? `<label>Emoji (Telegram er standard react emoji)</label><select onchange="rset(${i},'trigger.emoji',this.value)">` +
      S.reactions.map(e => `<option ${e===t.emoji?"selected":""}>${e}</option>`).join("") + `</select>`
    : `<label>Command nam (prefix chara, jemon: ban)</label><input type="text" value="${esc(t.name||"")}" onchange="rset(${i},'trigger.name',this.value)">`;
  const scope = `<label class="chk"><input type="checkbox" ${all?"checked":""} onchange="allScope(${i},this.checked)"> Sob group e</label>` +
    (all ? "" : (G||[]).map(g => `<label class="chk"><input type="checkbox" ${(r.groups||[]).includes(String(g.id))?"checked":""} onchange="gscope(${i},${g.id},this.checked)"> ${esc(g.title)}</label>`).join(""));
  return `<div class="panel">
    <div class="row"><label class="chk" style="margin:0"><input type="checkbox" ${r.enabled?"checked":""} onchange="rset(${i},'enabled',this.checked)"> Chalu</label>
      <input type="text" class="grow" value="${esc(r.name)}" onchange="rset(${i},'name',this.value)">
      <button class="sm red" onclick="delRule(${i})">Muche felo</button></div>
    <div class="two"><div><label>Ki korle (trigger)</label><select onchange="rtype(${i},this.value)">
      <option value="reaction" ${t.type==="reaction"?"selected":""}>Message e react</option>
      <option value="command" ${t.type==="command"?"selected":""}>Reply command</option></select></div>
      <div>${trig}</div></div>
    <div class="two"><div><label>Ke korle kaj hobe</label><select onchange="rset(${i},'who',this.value)">
      <option value="me" ${r.who==="me"?"selected":""}>Shudhu ami</option><option value="trusted" ${r.who==="trusted"?"selected":""}>Ami + trusted moderator</option></select></div>
      <div><label>&nbsp;</label><label class="chk"><input type="checkbox" ${r.confirm?"checked":""} onchange="rset(${i},'confirm',this.checked)"> Age confirm chao</label></div></div>
    <h3>Kon group e</h3><div>${scope}</div>
    <h3>Ki hobe (ekta ekta kore, serial e)</h3>
    ${r.actions.map((a,j) => actHTML(a,i,j)).join("")}
    <div style="margin-top:8px"><button class="sm sec" onclick="addAct(${i})">+ Action</button></div></div>`;
}
function renderRules(){
  if(!R){ $("tab_rules").innerHTML = ""; return; }
  $("tab_rules").innerHTML = `<div class="muted" style="margin-bottom:8px">Reaction e emoji ta group e allowed thakte hobe (group admin der react chalu rakhte hobe). Command: message e reply diye <b>${esc(S.settings.prefix)}ban</b> likho.</div>` +
    R.map(ruleHTML).join("") +
    `<div class="row"><button class="sec" onclick="addRule()">+ Notun rule</button><button onclick="saveRules()">Save rules</button></div><div class="msg" id="rmsg"></div>`;
}
async function saveRules(){
  const r = await api("api/rules_save", {rules:R});
  if(r.ok){ R = r.rules; renderRules(); toast("Rules save hoyeche"); } else toast(r.error, true);
}

/* ---------------- people ---------------- */
function renderPeople(){
  if(!TR){ $("tab_people").innerHTML = ""; return; }
  const permOpts = ["*"].concat(S.action_types);
  $("tab_people").innerHTML = `<h2>Trusted moderator</h2><div class="muted" style="margin-bottom:6px">Eder react / command e rule kaj korbe (rule e "Ami + trusted" bachle) — shudhu tader dewa adhikar onujayi.</div>` +
    TR.map((t,i) => `<div class="panel"><div class="two"><div><label>Telegram user ID</label><input type="number" value="${t.id}" onchange="TR[${i}].id=+this.value"></div>
      <div><label>Nam (shudhu tomar mone rakhar jonno)</label><input type="text" value="${esc(t.name||"")}" onchange="TR[${i}].name=this.value"></div></div>
      <div>${permOpts.map(p => `<label class="chk"><input type="checkbox" ${(t.perms||[]).includes(p)?"checked":""} onchange="tperm(${i},'${p}',this.checked)"> ${p==="*"?"Sob":(ACT_BN[p]||p)}</label>`).join("")}</div>
      <div style="margin-top:8px"><button class="sm red" onclick="TR.splice(${i},1);renderPeople()">Remove</button></div></div>`).join("") +
    `<div class="row"><button class="sec" onclick="TR.push({id:0,name:'',perms:['mute','warn','delete']});renderPeople()">+ Trusted</button></div>
    <h2>Sob group e ban kora (global ban)</h2>
    ${(S.gban||[]).length ? S.gban.map(g => `<div class="log"><b>${esc(g.name||g.id)}</b> <span class="muted">${g.id}</span>
      <div style="margin-top:5px"><button class="sm ghost" onclick="ungban(${g.id})">Tule nao</button></div></div>`).join("") : '<div class="muted">Kauke global ban kora hoyni (Members theke "Sob group e ban")</div>'}
    <h2>Surokkhito list (kokhono ban/mute hobe na)</h2>
    <div class="muted">Admin ra ager theke-i surokkhito. Onno kauke rakhte chaile user ID ek line e ekta.</div>
    <textarea id="prot" style="margin-top:6px">${esc(PR)}</textarea>
    <div class="row" style="margin-top:10px"><button onclick="savePeople()">Save</button></div>`;
}
async function ungban(id){ if(!confirm("Sob group theke unban korbe?")) return; const r = await api("api/do", {user:id, action:{type:"ungban"}}); toast(r.msg || "Hoyeche", !r.ok); refresh(true); inited.people = false; }
function tperm(i, p, on){ const s = new Set(TR[i].perms||[]); on ? s.add(p) : s.delete(p); TR[i].perms = Array.from(s); }
async function savePeople(){
  PR = $("prot").value;
  const prot = PR.split("\n").map(s => s.trim()).filter(Boolean).map(Number).filter(n => n);
  const r = await api("api/lists_save", {trusted:TR.filter(t => t.id), protected:prot});
  if(r.ok){ toast("Save hoyeche"); refresh(true); } else toast("Save hoyni", true);
}

/* ---------------- log ---------------- */
function renderLog(){
  $("tab_log").innerHTML = S.logs.length ? S.logs.map(l => `<div class="log ${l.kind==="action" && l.ok===false ? "bad" : l.kind}">
    <div class="muted">${fmtT(l.t)}${l.chat_title ? " · " + esc(l.chat_title) : ""}${l.rule ? " · " + esc(l.rule) : ""}</div>
    <div>${l.user_name ? "<b>" + esc(l.user_name) + "</b> — " : ""}${esc(l.msg)}</div>
    ${l.undo && l.ok ? `<div style="margin-top:5px"><button class="sm ghost" onclick="undoIt('${l.id}')">Undo</button></div>` : ""}</div>`).join("")
    : '<div class="muted">Ekhono kono log nai</div>';
}
async function undoIt(id){ const r = await api("api/undo", {id}); toast(r.msg, !r.ok); refresh(true); }

/* ---------------- settings ---------------- */
function renderSettings(){
  if(!ST){ $("tab_settings").innerHTML = ""; return; }
  const c = (k, n) => `<label class="chk"><input type="checkbox" id="s_${k}" ${ST[k]?"checked":""}> ${n}</label>`;
  const nb = (k, n) => `<div><label>${n}</label><input type="number" id="s_${k}" min="0" value="${ST[k]}"></div>`;
  $("tab_settings").innerHTML = `<div class="panel"><h3>Nirapotta</h3>
    ${c("dry_run","Dry-run (kono kaj hobe na, shudhu log e likhbe, test er jonno)")}<br>${c("confirm_all","Sob action e age confirm chao")}
    <div class="two">${nb("undo_seconds","React diye koto second er moddhe sariye nile bondho hobe (0 = off)")}${nb("max_actions_per_min","Minite sorboccho koyta action")}</div>
    ${nb("react_max_age_h","Koto ghonta er purano message e react e kaj hobe na (0 = off)")}</div>
    <div class="panel"><h3>Command</h3><div class="two"><div><label>Command prefix</label><input type="text" id="s_prefix" value="${esc(ST.prefix)}"></div><div></div></div>
    ${c("delete_command","Command dewar por oi message muche daw")}</div>
    <div class="panel"><h3>Warn</h3><div class="two">${nb("warn_limit","Koyta warn e shasti")}
    <div><label>Shasti ki</label><select id="s_warn_action"><option value="mute" ${ST.warn_action==="mute"?"selected":""}>Mute</option>
      <option value="ban" ${ST.warn_action==="ban"?"selected":""}>Ban</option><option value="kick" ${ST.warn_action==="kick"?"selected":""}>Kick</option></select></div></div>
    ${nb("warn_mute_min","Mute hole koto minit")}${c("notify_in_chat","Warn dile group e jaanao")}</div>
    <div class="panel"><h3>Aro</h3>${c("cas_check","Notun member ke CAS spam list e dekho (spammer hole ban)")}
    <label>Log group/channel (sob action er khobor ekhane jabe, khali = na)</label><input type="text" id="s_log_chat" value="${esc(ST.log_chat||"")}" placeholder="@mylogs ba -100..."></div>
    <div class="panel"><h3>Backup</h3><div class="row"><button class="sm sec" onclick="exportCfg()">Download</button>
    <button class="sm sec" onclick="$('impf').click()">Restore</button><input type="file" id="impf" accept=".json" class="hide" onchange="importCfg(this)"></div></div>
    <div class="panel"><h3>Bot (confirm bortone ar captcha er jonno, optional)</h3>
    <label>Bot token (@BotFather theke)</label><input type="text" id="s_bot_token" value="${esc(ST.bot_token)}" placeholder="123456:ABC...">
    <div class="muted" style="margin-top:6px">Bot ke ekbar /start dao, ar captcha chaile group e admin koro.</div></div>
    <div class="row"><button onclick="saveSettings()">Save settings</button></div>`;
}
async function saveSettings(){
  const o = {}, g = k => $("s_"+k);
  for(const k of ["dry_run","confirm_all","delete_command","notify_in_chat","cas_check"]) o[k] = g(k).checked;
  for(const k of ["undo_seconds","max_actions_per_min","react_max_age_h","warn_limit","warn_mute_min"]) o[k] = +g(k).value || 0;
  o.prefix = g("prefix").value || "."; o.log_chat = g("log_chat").value; o.warn_action = g("warn_action").value; o.bot_token = g("bot_token").value;
  const r = await api("api/settings_save", {settings:o});
  if(r.ok){ toast("Save hoyeche" + (r.bot ? " · bot " + r.bot : "")); inited.settings = false; refresh(true); } else toast("Save hoyni", true);
}

async function exportCfg(){
  const r = await api("api/export"); const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(r.data, null, 1)], {type:"application/json"}));
  a.download = "moderator-backup.json"; a.click();
}
async function importCfg(inp){
  const f = inp.files[0]; if(!f) return;
  try{ const d = JSON.parse(await f.text()); const r = await api("api/import", {data:d});
    toast(r.ok ? "Restore hoyeche" : r.error, !r.ok); inited = {rules:false, people:false, settings:false}; G = null; refresh(true);
  }catch(e){ toast("File thik na", true); }
  inp.value = "";
}

/* ---------------- main ---------------- */
function render(){
  if(!S) return;
  if(tab === "status") renderStatus();
  else { $("badge").textContent = S.status.replace("_"," "); $("badge").className = "badge b-" + S.status; $("who").textContent = S.me ? S.me + (S.bot ? "  ·  bot " + S.bot : "") : "Session connect hoyni"; }
  if(tab === "groups") renderGroups();
  if(tab === "rules") renderRules();
  if(tab === "people") renderPeople();
  if(tab === "log") renderLog();
  if(tab === "settings") renderSettings();
}
async function refresh(force){
  try{
    S = await api("api/state");
    if(!inited.rules){ R = JSON.parse(JSON.stringify(S.rules)); inited.rules = true; }
    if(!inited.people){ TR = JSON.parse(JSON.stringify(S.trusted)); PR = S.protected.join("\n"); inited.people = true; }
    if(!inited.settings){ ST = JSON.parse(JSON.stringify(S.settings)); inited.settings = true; }
    // sudhu je tab er data change hoy (status/log) seta auto refresh; form tab e input noshto hobe na
    if(force || tab === "status" || tab === "log") render();
    else { $("badge").textContent = S.status.replace("_"," "); $("badge").className = "badge b-" + S.status; }
  }catch(e){ $("badge").textContent = "offline"; }
}
renderTabs(); refresh(true); setInterval(() => { if(!document.activeElement || !["TEXTAREA","INPUT"].includes(document.activeElement.tagName)) refresh(false); }, 4000);
</script>
</body>
</html>
"""
