"""linkguard.py - LINK SHIELD

Jekono prokar link (http/https, www, t.me, wa.me, obfuscated "google[.]com",
"google dot com", zero-width diye lukaono, inline URL button, media caption,
edit kore boshano link, forward kora link) sathe sathe delete kore.

Ei file-i asol kaj kore - website er "Link Shield" panel eta ke control kore.
"""
import asyncio
import re
import time

import actions
import engine
from core import events, hub, types

# --------------------------------------------------------------------------
# 1) TLD list - ei list er upor bhor korei "link ache kina" dhora hoy
# --------------------------------------------------------------------------
CC = ("ad ae af ag ai al am ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bl bm bn bo bq br bs bt bv bw by bz "
      "ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cw cx cy cz de dj dk dm do dz ec ee eg eh er es et eu fi fj fk fm "
      "fo fr ga gb gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il im in io iq ir is it "
      "je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mf mg mh mk ml mm mn "
      "mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt "
      "pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so sr ss st su sv sx sy sz tc td tf tg th tj tk "
      "tl tm tn to tr tt tv tw tz ua ug uk um us uy uz va vc ve vg vi vn vu wf ws ye yt za zm zw").split()

GTLD = ("com net org edu gov mil int info biz name pro mobi asia cat coop jobs travel tel aero museum post arpa xxx "
        "app dev page site online shop store blog cloud tech space website xyz top club vip win bet casino poker slots "
        "live life world today news media agency digital studio design art photo pics gallery video tube stream radio "
        "music audio podcast games game play fun lol wow love dating date sexy porn adult chat forum community social "
        "network email mail web host hosting server data ai one zero plus best cool buzz sale deals discount market "
        "marketing money finance bank credit loan insurance legal lawyer doctor health clinic fitness gym school "
        "college university academy education training course learn study exam tutor science engineering works tools "
        "supply parts repair services service solutions systems support help care express delivery taxi rent rental "
        "estate properties homes house land farm garden food cafe coffee bar pub beer wine pizza restaurant kitchen "
        "recipe cook taste menu hotel tours holiday vacation flight cruise tickets events wedding party gift gifts toys "
        "baby kids family fashion style beauty spa hair skin shoes bags jewelry watch glasses clothes "
        "bitcoin crypto coin token nft wallet exchange mining trading forex investment income earn profit reward prize "
        "bonus lottery jackpot roulette cash win big win jackpot casino betting sport sports cricket football "
        "click link links url domain wap icu cyou sbs cam cyber cfd gdn day loan work men review country download "
        "racing science trade webcam rest quest monster bond wiki news tv online top buzz fun zone life "
        "id pk in bd us uk ru cn tk ml ga cf gq xyz top pw cc ws biz info io co me tv pro vc gd gg im je ly "
        "shop store app link click live vip win fun site online xyz top space website").split()

TLD = frozenset(CC + GTLD)

# space dewya obfuscation ("google . com") - ekhane shudhu ei common gulo dhora hobe
STRICT_TLD = frozenset(("com net org edu gov mil info biz xyz online site shop store app dev cloud tech top club vip "
                        "win icu cyou sbs in bd us uk ru cn io co me tv cc pk link click live space website fun icu day "
                        "loan work men cam bond cyou pro").split())

# popular host - space diye likhleo dhora porbe
POPULAR_HOST = ("telegram wa whatsapp chat.whatsapp fb facebook instagram insta youtube youtu tiktok "
                "twitter discord snapchat linkedin reddit pinterest onlyfans xvideos pornhub xnxx xhamster brazzers "
                "1xbet melbet linebet betwinner mostbet 22bet mosbet dafabet baji crickex jeetbuzz bdnews24 "
                "prothomalo kalerkantho banglanews24 jugantor ittefaq tbsnews dhakapost").split()

TLD_ALT = "|".join(sorted((re.escape(t) for t in TLD), key=len, reverse=True))
STRICT_ALT = "|".join(sorted((re.escape(t) for t in STRICT_TLD), key=len, reverse=True))
HOST_ALT = "|".join(sorted((re.escape(h) for h in POPULAR_HOST), key=len, reverse=True))

# --------------------------------------------------------------------------
# 2) Regex
# --------------------------------------------------------------------------
_ZW = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff\u180e\u00ad]")
_MAP = {ord("。"): ".", ord("．"): ".", ord("｡"): ".", ord("､"): ".", ord("،"): ".",
        ord("؛"): ".", ord("⸱"): ".", ord("․"): ".", ord("﹒"): "."}
_HXXP = re.compile(r"\bh\s*[x×]\s*[x×]\s*p\s*(?:s)?\s*:?\s*/{0,3}", re.I)
_BRACKET_DOT = re.compile(r"\s*[\[\(\{<]\s*(?:\.|dot|d0t|DOT|Dot)\s*[\]\)\}>]\s*")
_DOT_WORD = re.compile(r"(?<=[a-z0-9])\s+(?:dot|d0t)\s+(?=[a-z0-9])", re.I)
_POPULAR_SPACED = re.compile(r"(?<![a-z0-9])(" + HOST_ALT + r")\s*([\.\u2024\u3002])\s*", re.I)
_SCHEME = re.compile(r"(?<![a-z0-9])(?:https?|ftps?|tgs?|hxxps?|mailto)\s*:\s*/\s*/?", re.I)
_WWW_SPACED = re.compile(r"(?<![a-z0-9])(w\s*\.?\s*w\s*\.?\s*w)[ \t]*\.[ \t]*", re.I)
_TG = re.compile(r"(?<![a-z0-9])(?:t|telegram)\s*\.\s*me\b|telegram\s*\.\s*dog\b|(?<!\w)tg\s*://", re.I)
_TG_SLASH = re.compile(r"(?<![a-z0-9])t\s*\.\s*me\s*/\S+", re.I)
_DOMAIN = re.compile(
    r"(?<![@\w.\-/])((?:[a-z0-9\u09e6-\u09ef](?:[a-z0-9\-\u09e6-\u09ef]{0,61}[a-z0-9\u09e6-\u09ef])?\.)+"
    r"(?:" + TLD_ALT + r"))(?![a-z0-9\-])(?::\d{2,5})?(?:[/?#][^\s<>\"']*)?", re.I)
_DOMAIN_SPACED = re.compile(
    r"(?<![@\w.\-/])((?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)*[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?[ \t]{0,3}"
    r"\.[ \t]{0,3}(?:" + STRICT_ALT + r"))(?![a-z0-9\-])(?::\d{2,5})?(?:[/?#][^\s<>\"']*)?", re.I)
_IP = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?::\d{1,5})?(?:[/?#]\S*)?")
_EMAIL = re.compile(r"(?<![\w.\-])[\w.\-+]{1,64}@(?:[a-z0-9\-]+\.)+(?:" + TLD_ALT + r")", re.I)
_MENTION = re.compile(r"(?<!\w)@[A-Za-z][A-Za-z0-9_]{3,}")
_HOST = re.compile(r"(?<![@\w.\-/])(?:" + HOST_ALT + r")[ \t]{0,3}\.[ \t]{0,3}[a-z]{2,12}(?![a-z0-9\-])", re.I)

TRAIL = " \t.,;:!?)]}>\"'|~*_"
# file name hole link na (photo.jpg, video.mp4 ...)
_EXTS = ("jpg jpeg jfif png gif bmp webp svg ico tif tiff heic heif mp4 mkv avi mov wmv flv webm m4v 3gp "
         "mp3 wav ogg oga m4a aac flac opus amr pdf doc docx xls xlsx ppt pptx odt ods txt rtf csv json xml yaml "
         "html htm php js css py java kt c cpp cs go rs rb swift sh bat exe msi apk app deb rpm iso img dmg "
         "zip rar 7z tar gz bz2 xz lz4 sql db sqlite log bak tmp part crdownload").split()


def _clean(s):
    s = s.strip(TRAIL)
    s = s.strip("[]()<>\"'")
    return s


def _looks_file(link):
    """photo.jpg / video.mp4 - eigulo link na"""
    s = link.lower().strip()
    if any(x in s for x in ("http://", "https://", "www.", "//", "/")):
        return False
    s = s.split("?")[0].split("#")[0]
    if "." not in s:
        return False
    ext = s.rsplit(".", 1)[1]
    return ext in _EXTS


def prepare(text):
    """Text ke normal kore - zero-width, bhanga dot, hxxp sob thik kore"""
    t = _ZW.sub("", text or "")
    t = t.translate(_MAP)
    t = _HXXP.sub("http://", t)
    t = _BRACKET_DOT.sub(".", t)
    t = _DOT_WORD.sub(".", t)
    t = _POPULAR_SPACED.sub(r"\1.", t)
    t = _WWW_SPACED.sub("www.", t)
    return t


def _ip_ok(ip):
    try:
        return all(0 <= int(p) <= 255 for p in ip.split("."))
    except Exception:
        return False


def text_links(text, allow_mentions=False):
    """Text theke sob link ber kore (list of (link, reason))"""
    if not text:
        return []
    t = prepare(text)
    found = []

    def add(raw, why):
        s = _clean(raw)
        if len(s) < 4 or _looks_file(s):
            return
        low = s.lower()
        if any(low == f[0].lower() or low in f[0].lower() for f in found):
            return
        found.append((s, why))

    for m in _TG.finditer(t):
        add(m.group(0), "telegram link")
    for m in _SCHEME.finditer(t):
        add(t[m.start():m.start() + 60], "scheme")
    for m in _HOST.finditer(t):
        add(m.group(0), "popular host")
    for m in _DOMAIN.finditer(t):
        g = m.group(0)
        tld = re.sub(r"^.*\.", "", g.split("/")[0].split(":")[0].split("?")[0]).lower()
        left = g.split(".")[0].strip()
        if len(tld) <= 2 and len(left) < 4 and g.count(".") < 2 and "://" not in g and not g.lower().startswith("www."):
            continue  # "you.la" type bhul bondho
        add(g, "domain")
    for m in _DOMAIN_SPACED.finditer(t):  # "google . com" style
            g = m.group(0)
            labels = [x for x in re.sub(r"\s+", "", g).split(".") if x]
            left = labels[1] if (labels and labels[0] == "www" and len(labels) > 1) else (labels[0] if labels else "")
            if len(left) >= 5:
                add(g, "spaced domain")
    for m in _IP.finditer(t):
        if _ip_ok(m.group(1)):
            add(m.group(0), "ip")
    for m in _EMAIL.finditer(t):
        add(m.group(0), "email")
    if allow_mentions:
        for m in _MENTION.finditer(t):
            add(m.group(0), "mention")
    return _dedupe(found)


def _dedupe(pairs):
    """Boro link ta rakho, chhoto duplicate baad dao"""
    out, seen = [], set()
    for link, why in sorted(pairs, key=lambda x: -len(x[0])):
        k = link.lower().strip("/")
        if not k or k in seen:
            continue
        if any(k != o[0].lower().strip("/") and k in o[0].lower().strip("/") for o in out):
            continue
        seen.add(k)
        out.append((link, why))
    return out


def _walk_urls(obj, depth=0, out=None):
    """Reply markup er vitore lukaono URL gulo ber kore (version-proof)"""
    if out is None:
        out = []
    if obj is None or depth > 6:
        return out
    if isinstance(obj, str):
        return out
    if isinstance(obj, (list, tuple)):
        for x in obj:
            _walk_urls(x, depth + 1, out)
        return out
    for key in ("url", "webpage_url", "href"):
        v = getattr(obj, key, None)
        if isinstance(v, str) and len(v) > 3:
            out.append(v)
    for key in ("type", "rows", "buttons", "result", "webpage", "action"):
        v = getattr(obj, key, None)
        if v is not None and not isinstance(v, (str, int, float, bool, bytes)):
            _walk_urls(v, depth + 1, out)
    return out


def entity_links(msg):
    """Telegram entity diye dewa link (text hidden link soho)"""
    out = []
    text = getattr(msg, "message", None) or ""
    for e in (getattr(msg, "entities", None) or []):
        cls = type(e).__name__
        if cls in ("MessageEntityTextUrl",):
            u = getattr(e, "url", None)
            if u:
                out.append((u, "hidden link"))
        elif cls in ("MessageEntityUrl", "MessageEntityWebView", "MessageEntityWebPage"):
            try:
                out.append((text[e.offset:e.offset + e.length], "url entity"))
            except Exception:
                out.append(("url-entity", "url entity"))
        elif cls == "MessageEntityMention":
            try:
                out.append((text[e.offset:e.offset + e.length], "mention"))
            except Exception:
                pass
    return out


def button_links(msg):
    markup = getattr(msg, "reply_markup", None)
    if not markup:
        return []
    out = []
    for u in _walk_urls(markup):
        if u.startswith("http") or u.startswith("tg://") or "." in u:
            out.append((u, "button link"))
    return out


def scan_message(msg, allow_mentions=False):
    """Message theke sob link: (link, reason) list"""
    found = list(text_links(getattr(msg, "message", None) or "", allow_mentions))
    found += entity_links(msg)
    found += button_links(msg)
    if getattr(msg, "web_preview", None) is not None:
        found.append(("web preview", "webpage preview"))
    return _dedupe(found)


def has_link(text):
    return bool(text_links(text))


# --------------------------------------------------------------------------
# 3) Allow list
# --------------------------------------------------------------------------
def _host_of(link):
    s = re.sub(r"^[a-z]+://", "", (link or "").lower())
    s = s.split("@")[-1].split("/")[0].split("?")[0].split(":")[0]
    return s.strip(".")


def is_allowed(link, allow):
    if not allow:
        return False
    host = _host_of(link)
    for a in allow:
        a = (a or "").strip().lower()
        if not a:
            continue
        if a.startswith("re:"):
            try:
                if re.search(a[3:], link, re.I):
                    return True
            except re.error:
                continue
            continue
        a = re.sub(r"^[a-z]+://", "", a).split("/")[0].strip(".")
        if host == a or host.endswith("." + a) or (a in link.lower()):
            return True
    return False


# --------------------------------------------------------------------------
# 4) Policy
# --------------------------------------------------------------------------
def _cfg(chat_id):
    """Group + global config milie final link policy"""
    gc = hub.group_cfg(chat_id)
    lg = dict(gc.get("link_guard") or {})
    st = hub.cfg["settings"]
    # purano automod lock on thakle setao manbo
    old = ((gc.get("automod") or {}).get("locks") or {}).get("links") or {}
    if old.get("on") and not (gc.get("link_guard") or {}).get("on"):
        lg["on"] = True
        if old.get("action") and old["action"] != "strike":
            lg["mode"] = {"delete": "delete", "mute": "mute", "ban": "ban"}.get(old["action"], lg.get("mode", "strike"))
    explicit = str(chat_id) in (hub.cfg.get("groups") or {})
    if not explicit and not st.get("link_all_admin_groups", True):
        lg["on"] = False
    lg["_master"] = bool(st.get("link_guard", True))
    lg["_notice_on"] = bool(st.get("link_notice", True))
    lg["_notice_s"] = int(st.get("link_notice_s", 12) or 0)
    lg["_ban_after"] = int(st.get("auto_blacklist_after", 3) or 0)
    lg["_auto_bl"] = bool(st.get("auto_blacklist", True))
    lg["_block_edit"] = bool(st.get("link_block_edit", True))
    lg["_block_buttons"] = bool(st.get("link_block_buttons", True))
    return lg


def enabled(chat_id):
    lg = _cfg(chat_id)
    return bool(lg.get("on") and lg.get("_master"))


def _steps(lg):
    steps = [s for s in (lg.get("steps") or []) if isinstance(s, dict) and s.get("action")]
    return steps or [{"action": "warn", "mute_min": 0},
                     {"action": "mute", "mute_min": int(lg.get("mute_min") or 60)},
                     {"action": "ban", "mute_min": 0}]


def _action_for(lg, n):
    """n = koto nombor bar. -> (action, mute_min)"""
    mode = (lg.get("mode") or "strike").lower()
    ban_after = int(lg.get("ban_after") or 0)
    if mode == "strike":
        if ban_after and n >= ban_after:
            return "ban", 0
        step = _steps(lg)[min(max(n, 1), len(_steps(lg))) - 1]
        return step.get("action", "warn"), int(step.get("mute_min") or 0)
    if mode == "delete":
        return None, 0
    if mode == "warn":
        return ("ban", 0) if (ban_after and n >= ban_after) else ("warn", 0)
    if mode == "mute":
        return ("ban", 0) if (ban_after and n >= ban_after) else ("mute", int(lg.get("mute_min") or 60))
    if mode == "kick":
        return ("ban", 0) if (ban_after and n >= ban_after) else ("kick", 0)
    if mode == "ban":
        return "ban", 0
    return "warn", 0


def _notice_text(lg, ctx, links, n):
    tpl = (lg.get("notice") or "").strip() or "🚫 {name}, ei group e link pathano nishiddho! ({n}/{max})"
    txt = actions.fmt(tpl, {**ctx, "n": n, "max": int(lg.get("ban_after") or 0) or len(_steps(lg))})
    shown = ", ".join(l for l, _ in links[:2])
    if shown and "{link}" in txt:
        txt = txt.replace("{link}", shown)
    elif shown:
        txt = txt + "\n🔗 " + shown[:120]
    return txt


# --------------------------------------------------------------------------
# 5) Punish
# --------------------------------------------------------------------------
async def punish(chat_id, msg, links, gc, title="", by_edit=False):
    lg = _cfg(chat_id)
    st = hub.cfg["settings"]
    sender = getattr(msg, "sender_id", None)
    name = ""
    try:
        name = await hub.user_name(sender)
    except Exception:
        name = str(sender)
    ctx = {"chat": chat_id, "user": sender, "user_name": name, "chat_title": title or "",
           "by": hub.me_id, "msg_id": getattr(msg, "id", None), "kind": "link",
           "link": ", ".join(l for l, _ in links[:3])}

    n = hub.strike_add(f"L{chat_id}", sender, 24)
    maxn = int(lg.get("ban_after") or 0) or len(_steps(lg))
    act, mute_min = _action_for(lg, n)
    why = ", ".join(sorted({w for _, w in links})) or "link"
    dry = bool(st.get("dry_run"))

    # 1) sathe sathe delete (sob theke age ei kaj ta)
    deleted = False
    if not dry:
        deleted = await hub.delete_msgs(chat_id, [getattr(msg, "id", None)])

    hub.log(kind="action", rule="link-shield", action="link delete", chat=chat_id,
            chat_title=title, user=sender, user_name=name, by=hub.me_id, ok=deleted,
            msg=("Link delete (" + why + "): " + ", ".join(l for l, _ in links[:2])[:160]) if deleted
                else ("Link mileche kintu delete korte parlam na (" + why + ")"),
            undo=None)
    hub.bump(links=1, deleted=1 if deleted else 0, actions=1, chat=chat_id, chat_title=title,
             user=sender, user_name=name)

    if dry:
        hub.log(kind="dry", rule="link-shield", chat=chat_id, chat_title=title, user=sender,
                user_name=name, msg="Dry-run: link delete hoyni (dry_run bondho koro)")
        return

    acts = []
    if lg.get("_notice_on") and act not in ("ban", None):
        acts.append({"type": "reply", "text": _notice_text(lg, ctx, links, n), "no_reply_to": True,
                     "delete_after": int(lg.get("_notice_s") or 0)})
    if act == "warn":
        if not lg.get("_notice_on"):
            acts.append({"type": "reply", "text": _notice_text(lg, ctx, links, n), "no_reply_to": True,
                         "delete_after": int(lg.get("_notice_s") or 0)})
    elif act == "mute":
        acts.append({"type": "mute", "duration_min": mute_min or int(lg.get("mute_min") or 60)})
    elif act == "kick":
        acts.append({"type": "kick"})
    elif act == "ban":
        acts.append({"type": "ban", "duration_min": 0})
        if lg.get("_notice_on"):
            acts.append({"type": "reply", "text": _notice_text(lg, ctx, links, n), "no_reply_to": True,
                         "delete_after": int(lg.get("_notice_s") or 0)})
    await engine.run_now(acts, ctx, "link-shield")

    hub.bump(warns=1 if act == "warn" else 0, mutes=1 if act == "mute" else 0,
             bans=1 if act in ("ban", "kick") else 0, actions=0, chat=chat_id, chat_title=title,
             user=sender, user_name=name)

    # auto blacklist: bar bar link dile
    if lg.get("_auto_bl"):
        offn = hub.offender_count(sender)
        if int(lg.get("_ban_after") or 0) and offn >= int(lg["_ban_after"]) and not hub.blacklisted(sender):
            hub.blacklist_add(sender, name, f"{offn} bar link pathiyechhe")
            hub.log(kind="note", rule="link-shield", chat=chat_id, chat_title=title, user=sender,
                    user_name=name, msg=f"Auto blacklist: {name} ({n} bar link)")


# --------------------------------------------------------------------------
# 6) Handler
# --------------------------------------------------------------------------
async def _skip(chat_id, msg, gc):
    """True hole ei message niye kaj korbo na"""
    st = hub.cfg["settings"]
    if not st.get("link_guard", True):
        return True
    if not (gc.get("link_guard") or {}).get("on", True):
        return True
    if not hub.client:
        return True
    sender = getattr(msg, "sender_id", None)
    if not sender or sender <= 0 or sender == hub.me_id:
        return True
    if not await hub.can_delete(chat_id):
        return True
    lg = gc.get("link_guard") or {}
    if sender in hub.trusted_ids():
        return True
    if lg.get("exempt_admins", True) and await hub.is_protected(chat_id, sender):
        return True
    return False


async def _handle(event, edited=False):
    if not getattr(event, "is_group", False):
        return
    chat_id = event.chat_id
    msg = event.message
    text = getattr(msg, "message", None) or ""
    markup = getattr(msg, "reply_markup", None)
    if not text and not markup and getattr(msg, "web_preview", None) is None:
        return
    # blacklisted user er sob message delete
    sender = getattr(msg, "sender_id", None)
    if sender and sender > 0 and sender != hub.me_id and hub.blacklisted(sender):
        gc0 = hub.group_cfg(chat_id)
        if gc0.get("enabled", True) and await hub.can_delete(chat_id):
            ok = await hub.delete_msgs(chat_id, [getattr(msg, "id", None)])
            nm = datetime_now_name(sender)
            hub.log(kind="action", rule="blacklist", action="delete", chat=chat_id, user=sender,
                    user_name=nm, ok=ok, msg="Blacklist e ache, message delete")
            hub.bump(deleted=1 if ok else 0, actions=1, chat=chat_id, user=sender, user_name=nm)
            return

    links = scan_message(msg, allow_mentions=False)
    if not links:
        return
    gc = hub.group_cfg(chat_id)
    if not gc.get("enabled", True):
        return
    if await _skip(chat_id, msg, gc):
        return
    lg = gc.get("link_guard") or {}
    if not lg.get("block_buttons", True) and all(w == "button link" for _, w in links):
        return
    if not lg.get("block_edits", True) and edited:
        return
    if not lg.get("block_forward", True) and getattr(msg, "fwd_from", None) is not None:
        return
    allow = list(lg.get("allow") or [])
    left = [(l, w) for l, w in links if not is_allowed(l, allow)]
    if not left:
        return
    title = ""
    try:
        ent = await hub.entity(chat_id)
        title = getattr(ent, "title", "") or ""
    except Exception:
        title = str(chat_id)
    if not _claim(chat_id, getattr(msg, "id", None)):
        return
    await punish(chat_id, msg, left, gc, title, by_edit=edited)


def datetime_now_name(uid):
    try:
        return hub.names.get(uid) or str(uid)
    except Exception:
        return str(uid)


async def _on_msg(event):
    try:
        await _handle(event, False)
    except Exception as e:
        hub.log(kind="error", msg=f"linkguard: {type(e).__name__}: {e}")


async def _on_edit(event):
    try:
        await _handle(event, True)
    except Exception as e:
        hub.log(kind="error", msg=f"linkguard(edit): {type(e).__name__}: {e}")


_done = set()


def _claim(chat_id, msg_id):
    """Ek message ekbar-i process hobe"""
    key = (chat_id, msg_id)
    if key in _done:
        return False
    _done.add(key)
    if len(_done) > 4000:
        for k in list(_done)[:2000]:
            _done.discard(k)
    return True


def attach(hub_, client):
    client.add_event_handler(_on_msg, events.NewMessage(incoming=True))
    client.add_event_handler(_on_edit, events.MessageEdited(incoming=True))


# --------------------------------------------------------------------------
# 7) Test tool (website er "Link Test" er jonno)
# --------------------------------------------------------------------------
def test(text):
    links = text_links(text, allow_mentions=True)
    return {
        "text": text,
        "has_link": bool(links),
        "count": len(links),
        "links": [{"link": l, "why": w} for l, w in links],
        "normalized": prepare(text),
    }
