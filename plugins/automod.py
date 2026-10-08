"""plugins/automod.py - lock (link, media, inline button...), shobdo, flood, newbie, dhap-dhap shasti, auto reply"""
import re
import time
from collections import defaultdict, deque

import actions
import engine
from core import LOCK_NAMES, events, hub

KIND_BN = {
    "links": "link", "mention": "@mention", "hashtag": "hashtag", "email": "email", "phone": "phone number",
    "long": "onek lomba message", "emoji": "onek emoji", "inline_buttons": "inline button",
    "via_bot": "inline bot er message", "forward": "forward kora message", "photo": "chhobi",
    "video": "video", "sticker": "sticker", "gif": "GIF", "voice": "voice message", "video_note": "gol video",
    "audio": "audio", "document": "file", "poll": "poll", "contact": "contact", "location": "location",
    "game": "game", "words": "nishiddho shobdo", "flood": "onek druto message",
}
MEDIA_KINDS = ("photo", "video", "sticker", "gif", "voice", "video_note", "audio", "document", "poll",
               "contact", "location", "game")

_URL_RE = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/|tg://)", re.I)
_DOMAIN_RE = re.compile(
    r"\b[a-z0-9][a-z0-9-]{1,}\.(?:com|net|org|info|xyz|me|io|co|app|ly|link|site|online|top|click|shop|"
    r"store|club|live|bd|in|ru|tk|ml|ga|cf|gq|cc|tv|vip|fun|win|pw|ws|biz|us|uk|to|gl)\b", re.I)
_MENTION_RE = re.compile(r"(?<!\w)@[A-Za-z][A-Za-z0-9_]{3,}")
_HASHTAG_RE = re.compile(r"(?<!\w)#\w{2,}")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?<!\d)\+?\d[\d\s\-().]{8,}\d")
_EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\U0001F000-\U0001F2FF]")
_flood = defaultdict(deque)


def attach(hub_, client):
    client.add_event_handler(_on_message, events.NewMessage(incoming=True))


# ---------------- message theke tothyo ----------------
def facts_from(m):
    media = set()
    g = lambda n: getattr(m, n, None)  # noqa: E731
    if g("photo"):
        media.add("photo")
    if g("sticker"):
        media.add("sticker")
    if g("gif"):
        media.add("gif")
    if g("voice"):
        media.add("voice")
    if g("video_note"):
        media.add("video_note")
    if g("video") and not (media & {"sticker", "gif", "video_note"}):
        media.add("video")
    if g("audio") and "voice" not in media:
        media.add("audio")
    if g("poll"):
        media.add("poll")
    if g("contact"):
        media.add("contact")
    if g("geo"):
        media.add("location")
    if g("game"):
        media.add("game")
    if g("document") and not (media & {"sticker", "gif", "voice", "video_note", "video", "audio"}):
        media.add("document")
    markup = g("reply_markup")
    return {
        "text": g("raw_text") or g("message") or "",
        "ents": [type(x).__name__ for x in (g("entities") or [])],
        "forwarded": g("fwd_from") is not None,
        "buttons": type(markup).__name__ == "ReplyInlineMarkup",
        "via_bot": g("via_bot_id") is not None,
        "media": media,
    }


def _flood_hit(chat, user, count, seconds, now):
    q = _flood[(chat, user)]
    q.append(now)
    while q and now - q[0] > seconds:
        q.popleft()
    return len(q) >= count


def _word_hit(words, text):
    low = text.lower()
    for w in words:
        w = w.strip()
        if not w:
            continue
        if w.lower().startswith("re:"):
            try:
                if re.search(w[3:], text, re.I):
                    return True
            except re.error:
                continue
        elif w.lower() in low:
            return True
    return False


def _link_hit(f, allow):
    t = f["text"]
    low = t.lower()
    has = (bool(_URL_RE.search(t)) or bool(_DOMAIN_RE.search(t))
           or any(n in ("MessageEntityUrl", "MessageEntityTextUrl") for n in f["ents"]))
    if has and any(a.strip().lower() in low for a in allow if a.strip()):
        return False
    return has


def detect(am, f, now, chat, user, newbie=False):
    """Violation hole (kind, cfg) ferot dey, na hole None. cfg e 'action' ar 'mute_min' thake."""
    lk = {n: dict(c) for n, c in am["locks"].items()}
    if newbie:   # notun member: link/media block (delete)
        blocks = set(am["newbie"].get("block") or [])
        forced = []
        if "links" in blocks:
            forced.append("links")
        if "media" in blocks:
            forced.extend(MEDIA_KINDS)
        for n in forced:
            if not lk[n]["on"]:
                lk[n] = {"on": True, "action": "delete", "mute_min": 0}
    t = f["text"]
    checks = [
        ("links", lambda: _link_hit(f, am["links_allow"])),
        ("mention", lambda: bool(_MENTION_RE.search(t))),
        ("hashtag", lambda: bool(_HASHTAG_RE.search(t))),
        ("email", lambda: bool(_EMAIL_RE.search(t))),
        ("phone", lambda: bool(_PHONE_RE.search(t))),
        ("long", lambda: len(t) > int(am["long_max"])),
        ("emoji", lambda: len(_EMOJI_RE.findall(t)) > int(am["emoji_max"])),
        ("inline_buttons", lambda: f["buttons"]),
        ("via_bot", lambda: f["via_bot"]),
        ("forward", lambda: f["forwarded"]),
    ] + [(k, (lambda k=k: k in f["media"])) for k in MEDIA_KINDS]
    for kind, fn in checks:
        if lk[kind]["on"] and fn():
            return kind, lk[kind]
    wd = am["words"]
    if wd["on"] and _word_hit(wd["list"], t):
        return "words", wd
    fl = am["flood"]
    if fl["on"] and _flood_hit(chat, user, int(fl["count"]), int(fl["seconds"]), now):
        return "flood", fl
    return None


# ---------------- shasti (dhap dhap) ----------------
def pick_step(steps, n):
    steps = steps or [{"action": "mute", "mute_min": 60}]
    return steps[min(max(n, 1), len(steps)) - 1]


def build_actions(action, mute_min, am, n):
    """action: delete | strike | mute | ban -> action list (age message delete)"""
    acts = [{"type": "delete", "optional": True}]
    if action == "mute":
        acts.append({"type": "mute", "duration_min": int(mute_min or 60)})
    elif action == "ban":
        acts.append({"type": "ban", "duration_min": 0})
    elif action in ("strike", "warn"):
        st = am["strikes"]
        step = pick_step(st["steps"], n)
        a = step.get("action", "warn")
        if a == "warn":
            acts.append({"type": "reply", "text": st["warn_text"], "no_reply_to": True,
                         "delete_after": int(st.get("notify_delete_s", 15))})
        elif a == "mute":
            acts.append({"type": "mute", "duration_min": int(step.get("mute_min") or 60)})
        elif a == "kick":
            acts.append({"type": "kick"})
        elif a == "ban":
            acts.append({"type": "ban", "duration_min": 0})
    return acts


async def apply_penalty(chat_id, user_id, kind, cfg, am, msg_id=None):
    """Ekta violation er shasti. cfg = lock config (action, mute_min)"""
    action = cfg.get("action", "strike")
    n = 0
    if action in ("strike", "warn"):
        n = hub.strike_add(chat_id, user_id, int(am["strikes"].get("window_h", 24)))
    ctx = {"chat": chat_id, "user": user_id, "by": hub.me_id, "msg_id": msg_id, "msg_out": False,
           "kind": KIND_BN.get(kind, kind), "n": n, "max": len(am["strikes"]["steps"])}
    await engine.run_now(build_actions(action, cfg.get("mute_min"), am, n), ctx, f"automod:{kind}")


# ---------------- handler ----------------
async def _on_message(event):
    try:
        await _handle(event)
    except Exception as e:
        hub.log(kind="error", msg=f"automod: {type(e).__name__}: {e}")


async def _handle(event):
    if not event.is_group:
        return
    chat_id, sender = event.chat_id, event.sender_id
    gc = hub.group_cfg(chat_id)
    if not gc["enabled"] or not sender or sender < 0 or sender == hub.me_id:
        return
    if await actions.enforce_gban(chat_id, sender):
        return
    am = gc["automod"]
    exempt = None   # lazy
    m = event.message
    if am["enabled"]:
        exempt = sender in hub.trusted_ids() or await hub.is_protected(chat_id, sender)
        if not exempt:
            hrs = hub.joined_hours_ago(chat_id, sender)
            newbie = bool(am["newbie"]["on"] and hrs is not None and hrs < float(am["newbie"]["hours"]))
            hit = detect(am, facts_from(m), time.time(), chat_id, sender, newbie)
            if hit:
                kind, cfg = hit
                await apply_penalty(chat_id, sender, kind, cfg, am, m.id)
                return
    await _filters(event, gc)


_last_filter = {}


async def _filters(event, gc):
    text = (event.raw_text or "").lower()
    if not text or not gc["filters"]:
        return
    now = time.time()
    for f in gc["filters"]:
        key = (f.get("key") or "").strip().lower()
        if key and key in text and now - _last_filter.get((event.chat_id, key), 0) > 20:
            _last_filter[(event.chat_id, key)] = now
            await event.reply(actions.fmt(f.get("reply", ""), {"chat_title": ""}))
            return
