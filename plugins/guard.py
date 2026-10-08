"""plugins/guard.py - join protection: bot dhoka bondho, anti-raid, global ban, CAS, service message safai, night mode"""
import asyncio
import time
from collections import deque

import actions
from core import display_name, events, hub
from plugins import automod


def attach(hub_, client):
    client.add_event_handler(_on_action, events.ChatAction())


async def _del_service(event):
    try:
        mid = getattr(getattr(event, "action_message", None), "id", None)
        if mid:
            await hub.client.delete_messages(event.chat_id, [mid])
    except Exception:
        pass


async def _cas_banned(uid):
    try:
        import aiohttp
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
            async with s.get(f"https://api.cas.chat/check?user_id={uid}") as r:
                data = await r.json(content_type=None)
                return bool(data.get("ok"))
    except Exception:
        return False


async def _on_action(event):
    try:
        await _handle(event)
    except Exception as e:
        hub.log(kind="error", msg=f"guard: {type(e).__name__}: {e}")


async def _handle(event):
    chat_id = event.chat_id
    gc = hub.group_cfg(chat_id)
    if not gc["enabled"]:
        return
    clean = gc["clean"]
    joined = bool(event.user_joined or event.user_added)
    if joined:
        if clean["join"]:
            await _del_service(event)
        users = (await event.get_users()) or []
        adder = getattr(event, "added_by", None)
        adder_id = getattr(adder, "id", adder) if adder else None
        for u in users:
            if u.id == hub.me_id:
                continue
            await _on_new_user(event, gc, u, adder_id)
        await _antiraid(chat_id, gc, len(users))
    elif event.user_left or event.user_kicked:
        if clean["leave"]:
            await _del_service(event)
    elif getattr(event, "new_pin", False):
        if clean["pin"]:
            await _del_service(event)


async def _on_new_user(event, gc, u, adder_id):
    chat_id = event.chat_id
    if getattr(u, "bot", False):
        ab = gc["antibot"]
        if ab["on"]:
            allowed = False
            if ab["mode"] != "everyone" and adder_id:
                allowed = (adder_id == hub.me_id or adder_id in hub.trusted_ids()
                           or adder_id in await hub.admin_ids(chat_id, force=True))
            if not allowed:
                ctx = {"chat": chat_id, "user": u.id, "by": hub.me_id, "user_name": display_name(u)}
                await hub.fill_names(ctx)
                res = await actions.run({"type": "kick"}, ctx)
                hub.log(kind="action", rule="antibot", action="kick", chat=chat_id,
                        chat_title=ctx.get("chat_title", ""), user=u.id, user_name=ctx["user_name"],
                        by=hub.me_id, ok=res["ok"], msg="Bot dhokano bondho: " + res["msg"], undo=None)
                if ab["punish"] != "none" and adder_id and adder_id != hub.me_id:
                    am = gc["automod"]
                    cfg = {"action": ab["punish"] if ab["punish"] in ("mute", "ban") else "strike", "mute_min": 60}
                    await automod.apply_penalty(chat_id, adder_id, "bot add", cfg, am)
        return
    hub.mark_joined(chat_id, u.id)
    if await actions.enforce_gban(chat_id, u.id):
        return
    if hub.cfg["settings"].get("cas_check") and await _cas_banned(u.id):
        ctx = {"chat": chat_id, "user": u.id, "by": hub.me_id, "user_name": display_name(u)}
        await hub.fill_names(ctx)
        res = await actions.run({"type": "ban"}, ctx)
        hub.log(kind="action", rule="CAS", action="ban", chat=chat_id, chat_title=ctx.get("chat_title", ""),
                user=u.id, user_name=ctx["user_name"], by=hub.me_id, ok=res["ok"],
                msg="CAS spam list e ache: " + res["msg"], undo=res["undo"])


async def _antiraid(chat_id, gc, count):
    ar = gc["antiraid"]
    if not ar["on"] or count <= 0:
        return
    now = time.time()
    q = hub.raid_joins.setdefault(chat_id, deque())
    for _ in range(count):
        q.append(now)
    while q and now - q[0] > int(ar["seconds"]):
        q.popleft()
    if len(q) >= int(ar["joins"]) and str(chat_id) not in hub.locks:
        q.clear()
        res = await actions.run({"type": "lock", "duration_min": int(ar["lock_min"]), "perms": {}},
                                {"chat": chat_id, "by": hub.me_id})
        ctx = {"chat": chat_id}
        await hub.fill_names(ctx)
        hub.locks.get(str(chat_id), {}).update(by="raid")
        hub.save_locks()
        hub.log(kind="action", rule="antiraid", action="lock", chat=chat_id, chat_title=ctx.get("chat_title", ""),
                ok=res["ok"], msg="Raid dhora poreche, group lock: " + res["msg"], undo=res["undo"])
        await hub.notify_owner(f"🚨 Raid! {ctx.get('chat_title', chat_id)} lock kora hoyeche ({ar['lock_min']} min)")


# ---------------- background: lock expiry + night mode ----------------
def _hm(s):
    try:
        h, m = str(s).split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return 0


def in_window(now_min, start, end):
    if start == end:
        return False
    return start <= now_min < end if start < end else (now_min >= start or now_min < end)


async def sweep():
    now = time.time()
    for key, rec in list(hub.locks.items()):
        if rec.get("until") and now >= rec["until"]:
            await actions.unlock_chat(int(key))
            hub.log(kind="note", msg=f"Lock er somoy shesh, unlock: {key}")
    if not hub.client:
        return
    for key, g in list(hub.cfg["groups"].items()):
        gc = hub.group_cfg(int(key))
        nt = gc["night"]
        if not (nt["on"] and gc["enabled"]):
            continue
        local = int((now / 60 + int(nt.get("tz", 360))) % 1440)
        night = in_window(local, _hm(nt["from"]), _hm(nt["to"]))
        chat = int(key)
        was = hub.night_state.get(chat)
        if night and not was and str(chat) not in hub.locks:
            res = await actions.run({"type": "lock", "perms": {}, "duration_min": 0}, {"chat": chat, "by": hub.me_id})
            if res["ok"]:
                hub.locks[str(chat)]["by"] = "night"
                hub.save_locks()
            hub.night_state[chat] = True
            hub.log(kind="action", rule="night", action="lock", chat=chat, ok=res["ok"], msg="Night mode: " + res["msg"], undo=None)
        elif not night and was is not False:
            if hub.locks.get(str(chat), {}).get("by") == "night":
                res = await actions.run({"type": "unlock"}, {"chat": chat, "by": hub.me_id})
                hub.log(kind="action", rule="night", action="unlock", chat=chat, ok=res["ok"], msg="Night mode shesh: " + res["msg"], undo=None)
            hub.night_state[chat] = False


async def background(hub_):
    while True:
        await asyncio.sleep(30)
        try:
            if hub.client:
                await sweep()
        except Exception as e:
            hub.log(kind="error", msg=f"sweep: {type(e).__name__}: {e}")
