"""webapp.py - website er API (notun: stats, link test, quick toggle, bulk, broadcast)"""
import asyncio
import time

from aiohttp import web

import actions
import engine
import linkguard
from core import (ALLOWED_REACTIONS, CRYPTG, CRYPTG_ERR, DEFAULT_GROUP, DEFAULT_LINK_GUARD, DEFAULT_SETTINGS,
                  LOCK_NAMES, deep_merge, display_name, hub)
from ui import HTML

MASK = "•••"


def J(d):
    return web.json_response(d)


async def body(req):
    try:
        return await req.json()
    except Exception:
        return {}


def public_settings():
    s = dict(hub.cfg["settings"])
    s["bot_token"] = MASK if s.get("bot_token") else ""
    return s


async def index(req):
    return web.Response(text=HTML, content_type="text/html")


async def api_state(req):
    return J({
        "status": hub.status, "error": hub.error, "me": hub.me_name, "me_id": hub.me_id,
        "bot": hub.bot_status, "started": hub.started, "now": time.time(),
        "settings": public_settings(), "rules": hub.cfg["rules"],
        "trusted": hub.cfg["trusted"], "protected": hub.cfg["protected"],
        "pending": [{k: p[k] for k in ("id", "t", "summary")} for p in hub.pending.values()],
        "logs": list(hub.logs)[:200], "react_debug": list(hub.react_debug),
        "cryptg": CRYPTG, "cryptg_err": CRYPTG_ERR, "reactions": ALLOWED_REACTIONS,
        "action_types": actions.ACTION_TYPES, "captcha_pending": len(hub.captcha),
        "gban": hub.cfg["gban"], "locks_active": len(hub.locks),
        "link_defaults": DEFAULT_LINK_GUARD,
        "stats": hub.stats_public(),
        "blacklist": [{"id": int(k), **v} for k, v in hub.blacklist.items()][:200],
        "locked_chats": list(hub.locks.keys()),
        "version": "2.0",
    })


async def api_connect(req):
    s = ((await body(req)).get("session") or "").strip()
    if not s:
        return J({"ok": False, "error": "Session string dao"})
    ok = await hub.connect(s)
    return J({"ok": ok, "error": hub.error})


async def api_logout(req):
    await hub.logout()
    return J({"ok": True})


async def api_groups(req):
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro", "groups": []})
    try:
        groups = await hub.list_groups(force=req.query.get("force") == "1")
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}", "groups": []})
    out = []
    for g in groups:
        g = dict(g)
        g["cfg"] = hub.group_cfg(g["id"])
        out.append(g)
    return J({"ok": True, "groups": out})


def _clean_list(v):
    return [str(x).strip() for x in (v or []) if str(x).strip()]


def _int(v, lo=0, default=0):
    try:
        return max(lo, int(float(v)))
    except Exception:
        return max(lo, default)


def _hm(v, default):
    try:
        h, m = str(v).split(":")
        if 0 <= int(h) < 24 and 0 <= int(m) < 60:
            return f"{int(h):02d}:{int(m):02d}"
    except Exception:
        pass
    return default


def sanitize_link_guard(inc, base=None):
    lg = deep_merge(base or DEFAULT_LINK_GUARD, inc or {})
    lg["on"] = bool(lg.get("on", True))
    lg["exempt_admins"] = bool(lg.get("exempt_admins", True))
    lg["mode"] = lg["mode"] if lg.get("mode") in ("delete", "warn", "strike", "mute", "ban", "kick") else "strike"
    lg["mute_min"] = _int(lg.get("mute_min"), 1, 120)
    lg["ban_after"] = _int(lg.get("ban_after"), 0, 3)
    steps = []
    for x in lg.get("steps") or []:
        if not isinstance(x, dict):
            continue
        a = str(x.get("action", "")).lower()
        if a in ("warn", "mute", "kick", "ban"):
            steps.append({"action": a, "mute_min": _int(x.get("mute_min"), 0, 0) or (120 if a == "mute" else 0)})
    lg["steps"] = steps or [{"action": "warn", "mute_min": 0}, {"action": "mute", "mute_min": 120},
                            {"action": "ban", "mute_min": 0}]
    lg["notice"] = str(lg.get("notice") or DEFAULT_LINK_GUARD["notice"])[:600]
    lg["notice_s"] = _int(lg.get("notice_s"), 0, 12)
    lg["allow"] = [x.strip().lower()[:120] for x in _clean_list(lg.get("allow"))][:300]
    for k in ("block_buttons", "block_edits", "block_forward", "block_names"):
        lg[k] = bool(lg.get(k, True))
    return lg


def sanitize_group(inc):
    c = deep_merge(DEFAULT_GROUP, inc or {})
    am = c["automod"]
    c["enabled"] = bool(c["enabled"])
    c["rules_text"] = str(c.get("rules_text") or "")[:3000]
    c["link_guard"] = sanitize_link_guard(c.get("link_guard"))
    flt = []
    for f in c.get("filters") or []:
        try:
            k, r = str(f.get("key", "")).strip(), str(f.get("reply", "")).strip()
            if k and r:
                flt.append({"key": k[:60], "reply": r[:1500]})
        except Exception:
            pass
    c["filters"] = flt[:100]
    am["enabled"] = bool(am["enabled"])
    for n in LOCK_NAMES:
        L = am["locks"].setdefault(n, {})
        L["on"] = bool(L.get("on"))
        L["action"] = L.get("action") if L.get("action") in ("delete", "strike", "mute", "ban") else "strike"
        L["mute_min"] = _int(L.get("mute_min"), 1, 60)
    am["links_allow"] = _clean_list(am.get("links_allow"))
    am["long_max"] = _int(am.get("long_max"), 1, 1500)
    am["emoji_max"] = _int(am.get("emoji_max"), 1, 12)
    w = am["words"]
    w["on"] = bool(w.get("on"))
    w["list"] = _clean_list(w.get("list"))
    w["action"] = w.get("action") if w.get("action") in ("delete", "strike", "mute", "ban") else "strike"
    w["mute_min"] = _int(w.get("mute_min"), 1, 60)
    fl = am["flood"]
    fl["on"] = bool(fl.get("on"))
    fl["count"], fl["seconds"], fl["mute_min"] = _int(fl.get("count"), 2, 6), _int(fl.get("seconds"), 1, 8), _int(fl.get("mute_min"), 1, 10)
    fl["action"] = fl.get("action") if fl.get("action") in ("delete", "strike", "mute", "ban") else "mute"
    nb = am["newbie"]
    nb["on"] = bool(nb.get("on"))
    nb["hours"] = _int(nb.get("hours"), 1, 24)
    nb["block"] = [b for b in (nb.get("block") or []) if b in ("links", "media")]
    st = am["strikes"]
    st["window_h"] = _int(st.get("window_h"), 1, 24)
    steps = []
    for x in st.get("steps") or []:
        a = str(x.get("action", "")).lower()
        if a in ("warn", "mute", "kick", "ban"):
            steps.append({"action": a, "mute_min": _int(x.get("mute_min"), 0, 0) or (60 if a == "mute" else 0)})
    st["steps"] = steps or [{"action": "warn", "mute_min": 0}, {"action": "mute", "mute_min": 60}]
    st["warn_text"] = str(st.get("warn_text") or DEFAULT_GROUP["automod"]["strikes"]["warn_text"])[:500]
    st["notify_delete_s"] = _int(st.get("notify_delete_s"), 0, 15)
    ab = c["antibot"]
    ab["on"] = bool(ab.get("on"))
    ab["mode"] = ab.get("mode") if ab.get("mode") in ("non_admin", "everyone") else "non_admin"
    ab["punish"] = ab.get("punish") if ab.get("punish") in ("none", "warn", "mute", "ban") else "none"
    ar = c["antiraid"]
    ar["on"] = bool(ar.get("on"))
    ar["joins"], ar["seconds"], ar["lock_min"] = _int(ar.get("joins"), 2, 10), _int(ar.get("seconds"), 1, 30), _int(ar.get("lock_min"), 1, 10)
    nt = c["night"]
    nt["on"] = bool(nt.get("on"))
    nt["from"], nt["to"] = _hm(nt.get("from"), "23:00"), _hm(nt.get("to"), "06:00")
    nt["tz"] = max(-720, min(840, _int(nt.get("tz"), -720, 360)))
    for k in ("join", "leave", "pin"):
        c["clean"][k] = bool(c["clean"].get(k))
    wl = c["welcome"]
    wl["on"], wl["text"], wl["delete_after"] = bool(wl.get("on")), str(wl.get("text") or "")[:1000], _int(wl.get("delete_after"), 0, 60)
    cp = c["captcha"]
    cp["on"], cp["text"] = bool(cp.get("on")), str(cp.get("text") or "")[:500]
    cp["timeout_min"] = _int(cp.get("timeout_min"), 1, 5)
    cp["fail"] = "ban" if cp.get("fail") == "ban" else "kick"
    return c


async def api_group_save(req):
    b = await body(req)
    try:
        chat = str(int(b.get("chat")))
    except Exception:
        return J({"ok": False, "error": "chat id thik na"})
    try:
        cfg = sanitize_group(b.get("cfg"))
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}"})
    hub.cfg["groups"][chat] = cfg
    hub.save()
    return J({"ok": True, "cfg": cfg})


async def api_members(req):
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro", "members": []})
    try:
        chat = int(req.query.get("chat"))
        ent = await hub.entity(chat)
        out = []
        async for u in hub.client.iter_participants(ent, search=req.query.get("q", ""), limit=60):
            p = type(getattr(u, "participant", None)).__name__
            out.append({
                "id": u.id, "name": display_name(u), "username": getattr(u, "username", None),
                "bot": bool(getattr(u, "bot", False)),
                "admin": ("Admin" in p or "Creator" in p),
                "warns": hub.warn_get(chat, u.id),
                "blacklisted": hub.blacklisted(u.id),
                "links": hub.offender_count(u.id),
            })
        return J({"ok": True, "members": out})
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}", "members": []})


async def api_do(req):
    b = await body(req)
    act = b.get("action") or {}
    if act.get("type") not in actions.ACTION_TYPES:
        return J({"ok": False, "msg": "Ochena action"})
    if not hub.client:
        return J({"ok": False, "msg": "Age session connect koro"})
    try:
        chat = b.get("chat")
        ctx = {"chat": int(chat) if chat not in (None, "") else None, "user": int(b.get("user") or 0) or None,
               "by": hub.me_id, "msg_id": None, "num": b.get("num"), "text": str(b.get("text") or "")}
    except Exception:
        return J({"ok": False, "msg": "chat/user id thik na"})
    if ctx["chat"] is None and act.get("type") not in ("gban", "ungban"):
        return J({"ok": False, "msg": "Kon group e? chat id dao"})
    await engine.run_now([act], ctx, "website")
    last = hub.logs[0] if hub.logs else {}
    if hub.cfg["settings"].get("dry_run"):
        return J({"ok": True, "msg": "Dry-run: kichu hoyni"})
    return J({"ok": bool(last.get("ok")), "msg": last.get("msg", "")})


def clean_rule(r, i):
    t = r.get("trigger") or {}
    ttype = t.get("type") if t.get("type") in ("reaction", "command") else "reaction"
    trig = {"type": ttype}
    if ttype == "reaction":
        trig["emoji"] = str(t.get("emoji") or "")
    else:
        trig["name"] = str(t.get("name") or "").strip().lstrip(".").lower()
    acts = []
    for a in r.get("actions") or []:
        if a.get("type") not in actions.ACTION_TYPES:
            continue
        a = dict(a)
        for k in ("duration_min", "seconds", "delete_after"):
            if k in a:
                a[k] = _int(a.get(k), 0, 0)
        acts.append(a)
    gs = [str(x) for x in (r.get("groups") or [])]
    return {
        "id": str(r.get("id") or f"r_{int(time.time())}_{i}"),
        "name": str(r.get("name") or "Rule")[:60], "enabled": bool(r.get("enabled", True)),
        "trigger": trig, "who": r.get("who") if r.get("who") in ("me", "trusted") else "me",
        "groups": gs, "confirm": bool(r.get("confirm")), "actions": acts,
    }


async def api_rules_save(req):
    rules = (await body(req)).get("rules")
    if not isinstance(rules, list):
        return J({"ok": False, "error": "rules list lagbe"})
    try:
        hub.cfg["rules"] = [clean_rule(r, i) for i, r in enumerate(rules)]
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}"})
    hub.save()
    return J({"ok": True, "rules": hub.cfg["rules"]})


async def api_settings_save(req):
    inc = (await body(req)).get("settings") or {}
    cur = hub.cfg["settings"]
    old_tok = cur.get("bot_token", "")
    for k, dv in DEFAULT_SETTINGS.items():
        if k not in inc:
            continue
        v = inc[k]
        try:
            if k == "bot_token":
                if v == MASK:
                    continue
                cur[k] = str(v).strip()
            elif isinstance(dv, bool):
                cur[k] = bool(v)
            elif isinstance(dv, int):
                cur[k] = max(0, int(v))
            else:
                cur[k] = str(v)
        except Exception:
            pass
    if cur.get("warn_action") not in ("mute", "ban", "kick"):
        cur["warn_action"] = "mute"
    if not cur.get("prefix"):
        cur["prefix"] = "."
    hub.save()
    if cur.get("bot_token", "") != old_tok and hub.client:
        await hub.connect_bot()
    return J({"ok": True, "bot": hub.bot_status})


async def api_lists_save(req):
    b = await body(req)
    trusted = []
    for t in b.get("trusted") or []:
        try:
            trusted.append({"id": int(t["id"]), "name": str(t.get("name") or "")[:40],
                            "perms": [str(p) for p in (t.get("perms") or [])]})
        except Exception:
            pass
    prot = []
    for x in b.get("protected") or []:
        try:
            prot.append(int(x))
        except Exception:
            pass
    hub.cfg["trusted"], hub.cfg["protected"] = trusted, prot
    hub.save()
    return J({"ok": True})


async def api_undo(req):
    lid = (await body(req)).get("id")
    entry = next((e for e in hub.logs if e.get("id") == lid), None)
    if not entry or not entry.get("undo"):
        return J({"ok": False, "msg": "Undo kora jabe na"})
    res = await actions.undo(entry)
    if res["ok"]:
        entry["undo"] = None
    hub.log(kind="action", rule="undo", action="undo", chat=entry.get("chat"),
            chat_title=entry.get("chat_title", ""), user=entry.get("user"),
            user_name=entry.get("user_name", ""), by=hub.me_id, ok=res["ok"],
            msg="Undo: " + res["msg"], undo=None)
    return J(res)


async def api_confirm(req):
    b = await body(req)
    found = await engine.resolve_confirm(str(b.get("id")), bool(b.get("ok")))
    return J({"ok": found})


# ---------------- notun endpoint gulo ----------------
async def api_linktest(req):
    b = await body(req)
    return J({"ok": True, **linkguard.test(str(b.get("text") or ""))})


QUICK_KEYS = {
    # key -> (path, type)
    "link_guard.on": ("link_guard.on", bool),
    "link_guard.mode": ("link_guard.mode", str),
    "link_guard.exempt_admins": ("link_guard.exempt_admins", bool),
    "link_guard.notice_s": ("link_guard.notice_s", int),
    "link_guard.ban_after": ("link_guard.ban_after", int),
    "enabled": ("enabled", bool),
    "automod.enabled": ("automod.enabled", bool),
    "automod.locks.links.on": ("automod.locks.links.on", bool),
    "automod.flood.on": ("automod.flood.on", bool),
    "automod.words.on": ("automod.words.on", bool),
    "automod.newbie.on": ("automod.newbie.on", bool),
    "antibot.on": ("antibot.on", bool),
    "antiraid.on": ("antiraid.on", bool),
    "night.on": ("night.on", bool),
    "welcome.on": ("welcome.on", bool),
    "captcha.on": ("captcha.on", bool),
    "clean.join": ("clean.join", bool),
    "clean.leave": ("clean.leave", bool),
    "clean.pin": ("clean.pin", bool),
}


def _set_path(obj, path, val):
    ks = path.split(".")
    for k in ks[:-1]:
        obj = obj.setdefault(k, {})
    obj[ks[-1]] = val


async def api_quick(req):
    """Ek click e ekta setting on/off (form chara)"""
    b = await body(req)
    try:
        chat = str(int(b.get("chat")))
    except Exception:
        return J({"ok": False, "error": "chat id thik na"})
    key = str(b.get("key") or "")
    if key not in QUICK_KEYS:
        return J({"ok": False, "error": "Ochena key"})
    path, typ = QUICK_KEYS[key]
    val = b.get("value")
    try:
        val = bool(val) if typ is bool else (int(val) if typ is int else str(val))
    except Exception:
        val = False
    cfg = sanitize_group(hub.cfg["groups"].get(chat) or {})
    _set_path(cfg, path, val)
    cfg = sanitize_group(cfg)
    hub.cfg["groups"][chat] = cfg
    hub.save()
    return J({"ok": True, "key": key, "value": val, "cfg": cfg})


async def api_bulk(req):
    """Sob group e ek click e ekta setting (link ban sob group e chalu kora...)"""
    b = await body(req)
    key = str(b.get("key") or "")
    if key not in QUICK_KEYS:
        return J({"ok": False, "error": "Ochena key"})
    path, typ = QUICK_KEYS[key]
    try:
        val = bool(b.get("value")) if typ is bool else (int(b.get("value")) if typ is int else str(b.get("value")))
    except Exception:
        val = False
    chats = b.get("chats") or None
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro"})
    try:
        groups = await hub.list_groups()
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}"})
    n = 0
    for g in groups:
        if not g.get("admin"):
            continue
        if chats and str(g["id"]) not in {str(x) for x in chats}:
            continue
        cfg = sanitize_group(hub.cfg["groups"].get(str(g["id"])) or {})
        _set_path(cfg, path, val)
        hub.cfg["groups"][str(g["id"])] = sanitize_group(cfg)
        n += 1
    hub.save()
    return J({"ok": True, "n": n, "key": key, "value": val})


async def api_bulk_lock(req):
    """Sob admin group e lock / unlock"""
    b = await body(req)
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro"})
    want = bool(b.get("lock"))
    n = 0
    for g in await hub.list_groups():
        if not g.get("admin"):
            continue
        try:
            if want:
                await actions.run({"type": "lock", "perms": {}, "duration_min": 0},
                                  {"chat": g["id"], "by": hub.me_id})
            elif str(g["id"]) in hub.locks:
                await actions.unlock_chat(g["id"])
            n += 1
        except Exception:
            pass
        await asyncio.sleep(0.3)
    hub.log(kind="note", msg=f"{'Lock' if want else 'Unlock'} kora holo {n} ta group e")
    return J({"ok": True, "n": n})


async def api_broadcast(req):
    b = await body(req)
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro"})
    text = str(b.get("text") or "").strip()
    if not text:
        return J({"ok": False, "error": "Ki pathabo likho"})
    chats = b.get("chats") or []
    ok = bad = 0
    groups = await hub.list_groups()
    for g in groups:
        if not g.get("admin"):
            continue
        if chats and str(g["id"]) not in {str(x) for x in chats}:
            continue
        try:
            await hub.client.send_message(await hub.entity(g["id"]), text)
            ok += 1
        except Exception:
            bad += 1
        await asyncio.sleep(0.4)
    hub.log(kind="note", msg=f"Broadcast pathano holo: {ok} group e (fail {bad})")
    return J({"ok": True, "sent": ok, "failed": bad})


async def api_blacklist(req):
    b = await body(req)
    try:
        uid = int(b.get("id"))
    except Exception:
        return J({"ok": False, "error": "user id thik na"})
    if b.get("remove"):
        hub.blacklist_del(uid)
        return J({"ok": True, "removed": True})
    name = str(b.get("name") or "")
    if not name:
        try:
            name = await hub.user_name(uid)
        except Exception:
            name = str(uid)
    hub.blacklist_add(uid, name, str(b.get("reason") or "manually"))
    return J({"ok": True, "name": name})


async def api_speedtest(req):
    """Group e ekta test message pathiye dekhbe delete korte pare kina"""
    if not hub.client:
        return J({"ok": False, "error": "Age session connect koro"})
    b = await body(req)
    lines = []
    for g in await hub.list_groups():
        if not g.get("admin"):
            continue
        try:
            ent = await hub.entity(g["id"])
            can = await hub.has_right(ent, "delete_messages")
            lines.append({"chat": g["id"], "title": g["title"], "delete": bool(can)})
        except Exception as e:
            lines.append({"chat": g["id"], "title": g["title"], "delete": False, "error": str(e)[:60]})
    return J({"ok": True, "groups": lines})


async def api_export(req):
    data = {"settings": public_settings(), "rules": hub.cfg["rules"], "trusted": hub.cfg["trusted"],
            "protected": hub.cfg["protected"], "groups": hub.cfg["groups"], "gban": hub.cfg["gban"],
            "blacklist": hub.blacklist}
    data["settings"].pop("bot_token", None)
    return J({"ok": True, "data": data})


async def api_import(req):
    d = (await body(req)).get("data")
    if not isinstance(d, dict):
        return J({"ok": False, "error": "Backup data thik na"})
    try:
        if isinstance(d.get("rules"), list):
            hub.cfg["rules"] = [clean_rule(r, i) for i, r in enumerate(d["rules"])]
        if isinstance(d.get("groups"), dict):
            hub.cfg["groups"] = {str(int(k)): sanitize_group(v) for k, v in d["groups"].items()}
        if isinstance(d.get("settings"), dict):
            keep = hub.cfg["settings"].get("bot_token", "")
            for k, dv in DEFAULT_SETTINGS.items():
                if k in d["settings"] and k != "bot_token":
                    v = d["settings"][k]
                    hub.cfg["settings"][k] = bool(v) if isinstance(dv, bool) else (_int(v, 0, dv) if isinstance(dv, int) else str(v))
            hub.cfg["settings"]["bot_token"] = keep
        hub.cfg["trusted"] = [t for t in (d.get("trusted") or []) if isinstance(t, dict) and str(t.get("id", "")).lstrip("-").isdigit()]
        hub.cfg["protected"] = [int(x) for x in (d.get("protected") or []) if str(x).lstrip("-").isdigit()]
        hub.cfg["gban"] = [g for g in (d.get("gban") or []) if isinstance(g, dict) and str(g.get("id", "")).lstrip("-").isdigit()]
        if isinstance(d.get("blacklist"), dict):
            hub.blacklist = {str(k): v for k, v in d["blacklist"].items() if str(k).lstrip("-").isdigit()}
            hub.save_blacklist()
    except Exception as e:
        return J({"ok": False, "error": f"{type(e).__name__}: {e}"})
    hub.save()
    return J({"ok": True})


def make_app():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/api/state", api_state)
    app.router.add_get("/api/groups", api_groups)
    app.router.add_get("/api/members", api_members)
    app.router.add_get("/api/export", api_export)
    app.router.add_get("/api/speedtest", api_speedtest)
    for path, fn in (("connect", api_connect), ("logout", api_logout), ("group_save", api_group_save),
                     ("do", api_do), ("rules_save", api_rules_save), ("settings_save", api_settings_save),
                     ("lists_save", api_lists_save), ("undo", api_undo), ("confirm", api_confirm),
                     ("import", api_import), ("linktest", api_linktest), ("quick", api_quick),
                     ("bulk", api_bulk), ("broadcast", api_broadcast), ("blacklist", api_blacklist),
                     ("bulk_lock", api_bulk_lock)):
        app.router.add_post("/api/" + path, fn)
    return app
