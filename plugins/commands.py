"""plugins/commands.py - reply dia command (.ban .mute 30m .promote ...)"""
import re

import engine
import linkguard
from core import events, hub, parse_duration


def attach(hub_, client):
    client.add_event_handler(_on_message, events.NewMessage())


async def _on_message(event):
    try:
        await _handle(event)
    except Exception as e:
        hub.log(kind="error", msg=f"command: {type(e).__name__}: {e}")


async def _resolve_user(tok):
    try:
        ref = tok if tok.startswith("@") else int(tok)
        return (await hub.entity(ref)).id
    except Exception:
        return None


def parse_args(argstr, have_target):
    """-> (target_ref_token | None, duration_min | None, text, num | None)
    num = prothom shudhu-sonkhya (jemon .purge 50 / .slow 30)"""
    target_tok, dur, rest, num = None, None, [], None
    for tok in argstr.split():
        if not have_target and target_tok is None and (tok.startswith("@") or re.fullmatch(r"-?\d{5,}", tok)):
            target_tok = tok
        elif dur is None and parse_duration(tok) is not None:
            dur = parse_duration(tok)
            if num is None and tok.isdigit():
                num = int(tok)
        else:
            rest.append(tok)
    return target_tok, dur, " ".join(rest), num


async def _handle(event):
    text = event.raw_text or ""
    prefix = hub.cfg["settings"].get("prefix", ".") or "."
    if len(text) < 2 or not text.startswith(prefix) or not event.is_group:
        return
    by = event.sender_id
    m = re.match(rf"^{re.escape(prefix)}([A-Za-z0-9_]+)\s*(.*)$", text, re.S)
    if not m:
        return
    name, argstr = m.group(1).lower(), m.group(2).strip()
    chat_id = event.chat_id

    if name == "rules":   # shobai dekhte pare (nijer o)
        await _show_rules(event)
        return
    if by != hub.me_id and not engine.trusted_entry(by):
        return

    if name == "help":
        names = sorted({(r["trigger"].get("name") or "") for r in hub.cfg["rules"]
                        if r.get("enabled", True) and r["trigger"].get("type") == "command"})
        body = "Commands: " + ", ".join(prefix + n for n in names if n)
        if event.out:
            await event.edit(body)
        else:
            await event.reply(body)
        return

    # ---------------- notun niyontron command (rule lagbe na) ----------------
    if name in ("linktest", "link", "test"):
        res = linkguard.test(argstr)
        if res["has_link"]:
            body = "🔍 Link dhora poreche: " + str(res["count"]) + "\n" + "\n".join(
                f"• {x['link']}  ({x['why']})" for x in res["links"][:8])
        else:
            body = "✅ Ei text e kono link paoa jayni"
        await _say(event, body)
        return
    if name in ("shield", "linkban"):
        gc = hub.group_cfg(chat_id)
        lg = gc.get("link_guard") or {}
        arg = argstr.strip().lower()
        if arg in ("on", "chalu", "1"):
            hub.cfg["groups"].setdefault(str(chat_id), {})
            g = hub.cfg["groups"][str(chat_id)]
            g.setdefault("link_guard", {})["on"] = True
            hub.save()
            await _say(event, "🛡 Link Shield CHALU - ekhon theke jekono link sathe sathe delete hobe")
        elif arg in ("off", "bondho", "0"):
            hub.cfg["groups"].setdefault(str(chat_id), {})
            g = hub.cfg["groups"][str(chat_id)]
            g.setdefault("link_guard", {})["on"] = False
            hub.save()
            await _say(event, "🛡 Link Shield bondho kora hobe ei group e")
        else:
            st = hub.cfg["settings"]
            on = bool(lg.get("on", True) and st.get("link_guard", True))
            await _say(event, ("🛡 Link Shield: " + ("CHALU ✅" if on else "BONDHO ❌") +
                               "\nMode: " + str(lg.get("mode", "strike")) +
                               "\nAllow: " + (", ".join(lg.get("allow") or []) or "kichu na") +
                               "\nBodlate: " + prefix + "shield on / " + prefix + "shield off"))
        return
    if name in ("wl", "allow"):
        if not argstr.strip():
            await _say(event, "Ki likhbe: " + prefix + "wl youtube.com")
            return
        hub.cfg["groups"].setdefault(str(chat_id), {})
        g = hub.cfg["groups"][str(chat_id)]
        lst = g.setdefault("link_guard", {}).setdefault("allow", [])
        for d in argstr.split():
            d = d.strip().lower()
            if d and d not in lst:
                lst.append(d)
        hub.save()
        await _say(event, "✅ Allow list: " + (", ".join(lst) or "khali"))
        return
    if name in ("unwl", "unallow"):
        hub.cfg["groups"].setdefault(str(chat_id), {})
        g = hub.cfg["groups"][str(chat_id)]
        lst = g.setdefault("link_guard", {}).setdefault("allow", [])
        for d in argstr.split():
            d = d.strip().lower()
            if d in lst:
                lst.remove(d)
        hub.save()
        await _say(event, "Allow list: " + (", ".join(lst) or "khali"))
        return
    if name in ("bl", "blacklist"):
        reply = await event.get_reply_message() if event.is_reply else None
        tok, _d, _r, _n = parse_args(argstr, reply is not None)
        uid = reply.sender_id if reply else (await _resolve_user(tok) if tok else None)
        if not uid:
            if hub.blacklist:
                rows = list(hub.blacklist.items())[:20]
                await _say(event, "🚫 Blacklist:\n" + "\n".join(f"• {v.get('name') or k} ({k})" for k, v in rows))
            else:
                await _say(event, "Blacklist khali. Reply diye likho: " + prefix + "bl")
            return
        nm = await hub.user_name(uid)
        hub.blacklist_add(uid, nm, "manually")
        await _say(event, f"🚫 {nm} ke blacklist kora holo - er sob message delete hobe")
        return
    if name in ("unbl", "unblacklist"):
        reply = await event.get_reply_message() if event.is_reply else None
        tok, _d, _r, _n = parse_args(argstr, reply is not None)
        uid = reply.sender_id if reply else (await _resolve_user(tok) if tok else None)
        if not uid:
            await _say(event, "Reply diye likho ba id dao: " + prefix + "unbl 12345")
            return
        hub.blacklist_del(uid)
        await _say(event, "✅ Blacklist theke tule neoa holo")
        return
    if name in ("id", "ids"):
        reply = await event.get_reply_message() if event.is_reply else None
        lines = [f"👤 Tomar ID: {by}", f"💬 Ei chat ID: {chat_id}"]
        if reply:
            lines.append(f"🎯 Reply kora user ID: {reply.sender_id}")
        await _say(event, "\n".join(lines))
        return
    if name in ("stats", "stat"):
        st = hub.stats_public()["today"]
        await _say(event, "📊 Ajker hisheb:\n" +
                   "\n".join(f"• {k}: {v}" for k, v in st.items()) if st else "Aj ekhono kichu hoyni")
        return

    if not engine.find_rules("command", name, chat_id):
        return

    reply = await event.get_reply_message() if event.is_reply else None
    target_id = reply.sender_id if reply else None
    tok, dur, rest, num = parse_args(argstr, target_id is not None)
    if target_id is None and tok:
        target_id = await _resolve_user(tok)
    args = {"duration_min": dur, "text": rest, "num": num}
    n = engine.fire("command", name, chat_id, target_id, by, msg=reply, args=args)
    if n and hub.cfg["settings"].get("delete_command", True):
        try:
            await event.delete()
        except Exception:
            pass


async def _say(event, text):
    """Command er uttor (pathanor por nijei muchhe jay jodi setting thake)"""
    try:
        if event.out:
            await event.edit(text)
            return
        m = await event.reply(text)
        secs = int(hub.cfg["settings"].get("reply_delete_s", 0) or 0)
        if secs > 0:
            import asyncio

            async def _later():
                await asyncio.sleep(secs)
                try:
                    await m.delete()
                except Exception:
                    pass
            asyncio.create_task(_later())
    except Exception as e:
        hub.log(kind="error", msg=f"command reply: {type(e).__name__}: {e}")


_last_rules = {}


async def _show_rules(event):
    import time
    gc = hub.group_cfg(event.chat_id)
    txt = (gc.get("rules_text") or "").strip()
    if not gc.get("enabled", True) or not txt:
        return
    now = time.time()
    if now - _last_rules.get(event.chat_id, 0) < 30:
        return
    _last_rules[event.chat_id] = now
    await event.reply(txt)
