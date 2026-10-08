"""actions.py - ban, mute, promote ... sob kaj ekhane"""
import asyncio
import time
from datetime import datetime, timedelta, timezone

from core import DEFAULT_RIGHTS, FLOOD, flood_secs, functions, hub, types

RIGHT_BN = {
    "ban_users": "ban/mute korar", "delete_messages": "message delete korar",
    "add_admins": "admin banano", "invite_users": "invite korar", "pin_messages": "pin korar",
    "change_info": "group setting bodlanor",
}

ERRS = {
    "ChatAdminRequiredError": "Tomar admin adhikar nei",
    "UserAdminInvalidError": "Ei user admin, tar upor kaj kora jabe na",
    "ChatAdminInviteRequiredError": "Invite korar adhikar nei",
    "UserPrivacyRestrictedError": "User er privacy te add kora jay na",
    "UserNotMutualContactError": "User mutual contact na, add kora jay na",
    "UserIdInvalidError": "User paoa jayni",
    "PeerIdInvalidError": "Chat/User paoa jayni",
    "ChatWriteForbiddenError": "Ekhane pathano jabe na",
    "MessageDeleteForbiddenError": "Message delete korar adhikar nei",
    "UserCreatorError": "Group owner er upor kaj kora jay na",
    "RightForbiddenError": "Ei adhikar dewar onumoti nei",
    "ParticipantIdInvalidError": "User ei group e nai",
    "UserNotParticipantError": "User ei group e nai",
    "PeerFloodError": "Telegram onek add/message block koreche (PeerFlood), pore cheshta koro",
}


def ok(msg, undo=None):
    return {"ok": True, "msg": msg, "undo": undo}


def fail(msg):
    return {"ok": False, "msg": msg, "undo": None}


def readable(e):
    return ERRS.get(type(e).__name__) or f"{type(e).__name__}: {str(e)[:150]}"


class _D(dict):
    def __missing__(self, k):
        return "{" + k + "}"


def fmt(text, ctx):
    vals = _D(name=ctx.get("user_name", ""), user=ctx.get("user_name", ""), id=ctx.get("user", ""),
              group=ctx.get("chat_title", ""), by=ctx.get("by_name", ""),
              kind=ctx.get("kind", ""), n=ctx.get("n", ""), max=ctx.get("max", ""))
    try:
        return str(text).format_map(vals)
    except Exception:
        return str(text)


def _until(mins):
    try:
        mins = int(mins or 0)
    except Exception:
        mins = 0
    return datetime.now(timezone.utc) + timedelta(minutes=mins) if mins > 0 else None


async def _guard(ctx, right=None, protect=False, need_user=True):
    if need_user:
        if not ctx.get("user"):
            return fail("Target user paoa jayni (message e reply dao ba @user likho)")
        if ctx["user"] == hub.me_id:
            return fail("Nijer upor kaj kora jabe na")
    ent = await hub.entity(ctx["chat"])
    if right and await hub.has_right(ent, right) is False:
        return fail("Ei group e tomar " + RIGHT_BN.get(right, right) + " adhikar nei")
    if protect and await hub.is_protected(ctx["chat"], ctx["user"]):
        return fail("Ei user surokkhito (admin / protected list e ache)")
    return None


async def _delete_all(ent, uid):
    if isinstance(ent, types.Channel):
        try:
            await hub.client(functions.channels.DeleteParticipantHistoryRequest(channel=ent, participant=uid))
            return -1
        except Exception:
            pass
    ids = []
    async for m in hub.client.iter_messages(ent, from_user=uid, limit=300):
        ids.append(m.id)
    if ids:
        await hub.client.delete_messages(ent, ids)
    return len(ids)


# ---------------- handlers ----------------
async def a_ban(act, ctx):
    g = await _guard(ctx, "ban_users", protect=True)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    mins = ctx.get("duration_min") or act.get("duration_min") or 0
    await hub.client.edit_permissions(ent, ctx["user"], until_date=_until(mins), view_messages=False)
    extra = ""
    if act.get("delete_history"):
        await _delete_all(ent, ctx["user"])
        extra = " + sob message muchlo"
    return ok("Ban" + (f" ({int(mins)} min)" if mins else "") + extra,
              {"type": "unban", "chat": ctx["chat"], "user": ctx["user"]})


async def a_mute(act, ctx):
    g = await _guard(ctx, "ban_users", protect=True)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    mins = ctx.get("duration_min") or act.get("duration_min") or 0
    await hub.client.edit_permissions(
        ent, ctx["user"], until_date=_until(mins), send_messages=False, send_media=False,
        send_stickers=False, send_gifs=False, send_games=False, send_inline=False,
        embed_link_previews=False, send_polls=False)
    return ok("Mute" + (f" ({int(mins)} min)" if mins else " (cholbe jotokkhon na unmute kori)"),
              {"type": "unmute", "chat": ctx["chat"], "user": ctx["user"]})


async def a_unban(act, ctx):
    g = await _guard(ctx, "ban_users")
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    await hub.client.edit_permissions(ent, ctx["user"])
    return ok("Unban/Unmute hoyeche")


a_unmute = a_unban


async def a_kick(act, ctx):
    g = await _guard(ctx, "ban_users", protect=True)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    await hub.client.kick_participant(ent, ctx["user"])
    return ok("Kick hoyeche (abar join korte parbe)")


async def a_warn(act, ctx):
    g = await _guard(ctx, "ban_users", protect=True)
    if g:
        return g
    st = hub.cfg["settings"]
    limit = max(1, int(st.get("warn_limit", 3)))
    n = hub.warn_add(ctx["chat"], ctx["user"], 1)
    msg = f"Warn {n}/{limit}"
    if st.get("notify_in_chat"):
        try:
            ent = await hub.entity(ctx["chat"])
            await hub.client.send_message(ent, f"⚠ {ctx.get('user_name', '')} — warn {n}/{limit}")
        except Exception:
            pass
    if n >= limit:
        hub.warn_reset(ctx["chat"], ctx["user"])
        kind = st.get("warn_action", "mute")
        if kind not in ("ban", "mute", "kick"):
            kind = "mute"
        res = await run({"type": kind, "duration_min": int(st.get("warn_mute_min", 1440))}, ctx)
        return {"ok": res["ok"], "msg": msg + " -> limit shesh, " + res["msg"], "undo": res["undo"]}
    return ok(msg, {"type": "unwarn", "chat": ctx["chat"], "user": ctx["user"]})


async def a_unwarn(act, ctx):
    if not ctx.get("user"):
        return fail("Target user paoa jayni")
    n = hub.warn_add(ctx["chat"], ctx["user"], -1)
    return ok(f"Warn kombe gelo, ekhon {n}")


async def a_delete(act, ctx):
    mid = ctx.get("msg_id")
    if not mid:
        return fail("Kon message delete korbo? (message e reply dao)")
    ent = await hub.entity(ctx["chat"])
    if not ctx.get("msg_out") and await hub.has_right(ent, "delete_messages") is False:
        return fail("Ei group e tomar message delete korar adhikar nei")
    await hub.client.delete_messages(ent, [mid])
    return ok("Message muche dewa hoyeche")


async def a_delete_all(act, ctx):
    g = await _guard(ctx, "delete_messages", protect=True)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    n = await _delete_all(ent, ctx["user"])
    return ok("Oi user er sob message muche dewa hoyeche" if n < 0 else f"{n} ta message muche dewa hoyeche")


async def a_promote(act, ctx):
    g = await _guard(ctx, "add_admins")
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    rt = dict(DEFAULT_RIGHTS)
    rt.update(act.get("rights") or {})
    title = fmt(act.get("title") or "", ctx)[:16] or None
    await hub.client.edit_admin(
        ent, ctx["user"], is_admin=True, title=title,
        change_info=bool(rt["change_info"]), delete_messages=bool(rt["delete_messages"]),
        ban_users=bool(rt["ban_users"]), invite_users=bool(rt["invite_users"]),
        pin_messages=bool(rt["pin_messages"]), add_admins=bool(rt["add_admins"]),
        manage_call=bool(rt["manage_call"]), anonymous=bool(rt["anonymous"]))
    return ok("Admin banano hoyeche" + (f" ({title})" if title else ""),
              {"type": "demote", "chat": ctx["chat"], "user": ctx["user"]})


async def a_demote(act, ctx):
    g = await _guard(ctx, "add_admins")
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    await hub.client.edit_admin(
        ent, ctx["user"], is_admin=False, change_info=False, delete_messages=False,
        ban_users=False, invite_users=False, pin_messages=False, add_admins=False,
        manage_call=False, anonymous=False)
    return ok("Admin theke namano hoyeche")


async def a_add_to_group(act, ctx):
    if not ctx.get("user"):
        return fail("Target user paoa jayni")
    try:
        target_id = int(act.get("target_group"))
    except Exception:
        return fail("Kon group e add korbo ta set kora nai")
    tgt = await hub.entity(target_id)
    if await hub.has_right(tgt, "invite_users") is False:
        return fail("Oi group e tomar invite korar adhikar nei")
    try:
        if isinstance(tgt, types.Channel):
            await hub.client(functions.channels.InviteToChannelRequest(tgt, [ctx["user"]]))
        else:
            await hub.client(functions.messages.AddChatUserRequest(chat_id=tgt.id, user_id=ctx["user"], fwd_limit=50))
        return ok("Group e add kora hoyeche: " + getattr(tgt, "title", str(target_id)))
    except Exception as e:
        if type(e).__name__ not in ("UserPrivacyRestrictedError", "UserNotMutualContactError",
                                    "UserChannelsTooMuchError", "UserKickedError"):
            raise
        # privacy: invite link pathai
        res = await hub.client(functions.messages.ExportChatInviteRequest(peer=tgt))
        text = fmt(act.get("text") or "Ei group e join koro: {link}", ctx).replace("{link}", res.link)
        await hub.client.send_message(ctx["user"], text)
        return ok("Privacy er karone add hoyni, DM e invite link pathiyechi")


async def a_dm(act, ctx):
    if not ctx.get("user"):
        return fail("Target user paoa jayni")
    text = fmt(act.get("text") or "Hi {name}", ctx)
    await hub.client.send_message(ctx["user"], text)
    return ok("DM pathano hoyeche")


async def _del_later(ent, mid, secs):
    await asyncio.sleep(secs)
    try:
        await hub.client.delete_messages(ent, [mid])
    except Exception:
        pass


async def a_reply(act, ctx):
    ent = await hub.entity(ctx["chat"])
    text = fmt(act.get("text") or "OK", ctx)
    m = await hub.client.send_message(
        ent, text, reply_to=None if act.get("no_reply_to") else ctx.get("msg_id"))
    da = int(act.get("delete_after") or 0)
    if da > 0:
        asyncio.create_task(_del_later(ent, m.id, da))
    return ok("Group e message pathano hoyeche")


async def a_pin(act, ctx):
    if not ctx.get("msg_id"):
        return fail("Kon message pin korbo? (message e reply dao)")
    ent = await hub.entity(ctx["chat"])
    if await hub.has_right(ent, "pin_messages") is False:
        return fail("Ei group e tomar pin korar adhikar nei")
    await hub.client.pin_message(ent, ctx["msg_id"])
    return ok("Pin kora hoyeche")


async def a_unpin(act, ctx):
    ent = await hub.entity(ctx["chat"])
    await hub.client.unpin_message(ent, ctx.get("msg_id"))
    return ok("Unpin kora hoyeche")


# ---------------- notun: restrict / lock / slowmode / purge / gban ----------------
PERM_FLAGS = ["send_messages", "send_media", "send_stickers", "send_gifs", "send_games", "send_inline",
              "embed_link_previews", "send_polls", "change_info", "invite_users", "pin_messages"]
BANNED_FIELDS = ["send_messages", "send_media", "send_stickers", "send_gifs", "send_games", "send_inline",
                 "embed_links", "send_polls", "change_info", "invite_users", "pin_messages"]
SEND_BANNED = BANNED_FIELDS[:8]
VALID_SLOW = [0, 10, 30, 60, 300, 900, 3600]


async def a_restrict(act, ctx):
    """Kisu korte parbe na: default = shudhu dekhte parbe, message dite parbe na"""
    g = await _guard(ctx, "ban_users", protect=True)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    perms = act.get("perms") or {}
    kw = {f: bool(perms.get(f, False)) for f in PERM_FLAGS}
    mins = ctx.get("duration_min") or act.get("duration_min") or 0
    await hub.client.edit_permissions(ent, ctx["user"], until_date=_until(mins), **kw)
    readonly = not any(kw[f] for f in PERM_FLAGS[:8])
    return ok(("Read-only (shudhu dekhte parbe)" if readonly else "Restrict") + (f" ({int(mins)} min)" if mins else ""),
              {"type": "unmute", "chat": ctx["chat"], "user": ctx["user"]})


def _flags_of(ent):
    dbr = getattr(ent, "default_banned_rights", None)
    return {f: bool(getattr(dbr, f, False)) for f in BANNED_FIELDS}


async def _set_default_rights(ent, banned):
    rights = types.ChatBannedRights(until_date=None, **{f: bool(banned.get(f, False)) for f in BANNED_FIELDS})
    await hub.client(functions.messages.EditChatDefaultBannedRightsRequest(peer=ent, banned_rights=rights))


async def lock_chat(chat_id, perms, mins, by="manual"):
    ent = await hub.entity(chat_id)
    key = str(chat_id)
    prev = hub.locks[key]["prev"] if key in hub.locks else _flags_of(ent)
    banned = dict(prev)
    for f in SEND_BANNED:
        allowed_key = "embed_link_previews" if f == "embed_links" else f
        banned[f] = not bool((perms or {}).get(allowed_key, False))
    await _set_default_rights(ent, banned)
    hub.locks[key] = {"until": time.time() + int(mins) * 60 if mins else 0, "prev": prev, "by": by}
    hub.save_locks()


async def unlock_chat(chat_id):
    ent = await hub.entity(chat_id)
    rec = hub.locks.pop(str(chat_id), None)
    await _set_default_rights(ent, rec["prev"] if rec else {f: False for f in BANNED_FIELDS})
    hub.save_locks()


async def a_lock(act, ctx):
    g = await _guard(ctx, "ban_users", need_user=False)
    if g:
        return g
    mins = ctx.get("duration_min") or act.get("duration_min") or 0
    await lock_chat(ctx["chat"], act.get("perms") or {}, mins)
    return ok("Group lock kora hoyeche" + (f" ({int(mins)} min)" if mins else ""),
              {"type": "unlock", "chat": ctx["chat"], "user": None})


async def a_unlock(act, ctx):
    g = await _guard(ctx, "ban_users", need_user=False)
    if g:
        return g
    await unlock_chat(ctx["chat"])
    return ok("Group unlock kora hoyeche")


async def a_slowmode(act, ctx):
    g = await _guard(ctx, "change_info", need_user=False)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    if not isinstance(ent, types.Channel):
        return fail("Slowmode shudhu supergroup e hoy")
    sec = ctx.get("num") if ctx.get("num") is not None else act.get("seconds", 0)
    sec = min(VALID_SLOW, key=lambda v: abs(v - int(sec or 0)))
    await hub.client(functions.channels.ToggleSlowModeRequest(channel=ent, seconds=sec))
    return ok(f"Slowmode {sec} second" if sec else "Slowmode bondho")


async def a_purge(act, ctx):
    g = await _guard(ctx, "delete_messages", need_user=False)
    if g:
        return g
    ent = await hub.entity(ctx["chat"])
    ids = []
    if ctx.get("msg_id"):
        async for m in hub.client.iter_messages(ent, min_id=ctx["msg_id"] - 1, limit=500):
            ids.append(m.id)
    else:
        n = int(ctx.get("num") or 0)
        if n <= 0:
            return fail("Message e reply dao ba sonkhya likho (jemon .purge 50)")
        async for m in hub.client.iter_messages(ent, limit=min(n, 500)):
            ids.append(m.id)
    for i in range(0, len(ids), 100):
        await hub.client.delete_messages(ent, ids[i:i + 100])
    return ok(f"{len(ids)} ta message muche dewa hoyeche")


async def _each_group(kind, uid):
    done = total = 0
    for gr in await hub.list_groups():
        if not gr["rights"].get("ban_users") or not hub.group_cfg(gr["id"]).get("enabled", True):
            continue
        total += 1
        res = await run({"type": kind}, {"chat": gr["id"], "user": uid, "by": hub.me_id})
        done += 1 if res["ok"] else 0
        await asyncio.sleep(0.4)
    return done, total


async def a_gban(act, ctx):
    uid = ctx.get("user")
    if not uid:
        return fail("Target user paoa jayni")
    if uid == hub.me_id or uid in {int(x) for x in hub.cfg["protected"]}:
        return fail("Ei user surokkhito")
    if uid not in hub.gban_ids():
        hub.cfg["gban"].append({"id": uid, "name": ctx.get("user_name", ""), "reason": ctx.get("text", ""),
                                "t": time.time()})
        hub.save()
    done, total = await _each_group("ban", uid)
    return ok(f"Global ban: {done}/{total} ta group e ban hoyeche",
              {"type": "ungban", "chat": ctx.get("chat"), "user": uid})


async def a_ungban(act, ctx):
    uid = ctx.get("user")
    if not uid:
        return fail("Target user paoa jayni")
    hub.cfg["gban"] = [g for g in hub.cfg["gban"] if int(g.get("id", 0)) != uid]
    hub.save()
    done, total = await _each_group("unban", uid)
    return ok(f"Global ban tule newa hoyeche: {done}/{total} ta group e unban")


async def enforce_gban(chat_id, uid):
    """Global ban list e thakle ei group e sathe sathe ban"""
    if uid not in hub.gban_ids():
        return False
    ctx = {"chat": chat_id, "user": uid, "by": hub.me_id}
    await hub.fill_names(ctx)
    res = await run({"type": "ban"}, ctx)
    hub.log(kind="action", rule="gban", action="ban", chat=chat_id, chat_title=ctx.get("chat_title", ""),
            user=uid, user_name=ctx.get("user_name", ""), by=hub.me_id, ok=res["ok"],
            msg="Global ban list e ache: " + res["msg"], undo=res["undo"])
    return True


HANDLERS = {
    "ban": a_ban, "mute": a_mute, "unban": a_unban, "unmute": a_unmute, "kick": a_kick,
    "warn": a_warn, "unwarn": a_unwarn, "delete": a_delete, "delete_all": a_delete_all,
    "promote": a_promote, "demote": a_demote, "add_to_group": a_add_to_group,
    "dm": a_dm, "reply": a_reply, "pin": a_pin, "unpin": a_unpin,
    "restrict": a_restrict, "lock": a_lock, "unlock": a_unlock, "slowmode": a_slowmode,
    "purge": a_purge, "gban": a_gban, "ungban": a_ungban,
}

ACTION_TYPES = list(HANDLERS.keys())


async def run(act, ctx):
    fn = HANDLERS.get(act.get("type"))
    if not fn:
        return fail("Ochena action: " + str(act.get("type")))
    try:
        try:
            return await fn(act, ctx)
        except FLOOD as e:
            await asyncio.sleep(min(flood_secs(e), 120) + 1)
            return await fn(act, ctx)
    except Exception as e:
        return fail(readable(e))


async def undo(entry):
    u = entry.get("undo")
    if not u:
        return fail("Eta undo kora jay na")
    ctx = {"chat": u.get("chat"), "user": u.get("user"), "by": hub.me_id}
    await hub.fill_names(ctx)
    return await run({"type": u["type"]}, ctx)
