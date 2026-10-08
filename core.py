"""core.py - shared state, config, helpers (sob module eta use kore)"""
import asyncio
import importlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

# ---- cryptg: Telethon er speed er jonno. Telethon import er AGE install kore nei ----
CRYPTG_ERR = ""


def _has_cryptg():
    try:
        import cryptg  # noqa: F401
        return True
    except ImportError:
        return False


CRYPTG = _has_cryptg()
if not CRYPTG:
    try:
        _libdir = os.path.join(BASE, "pylibs_extra")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
             "--target", _libdir, "cryptg"],
            timeout=300, check=True, capture_output=True,
        )
        if _libdir not in sys.path:
            sys.path.insert(0, _libdir)
        importlib.invalidate_caches()
        CRYPTG = _has_cryptg()
    except Exception as _e:
        CRYPTG_ERR = str(_e)[-200:]

from telethon import Button, TelegramClient, events, functions, types, utils  # noqa: E402
from telethon.errors import FloodWaitError  # noqa: E402
from telethon.sessions import StringSession  # noqa: E402

FLOOD = (FloodWaitError,)
try:
    from telethon.errors import FloodError as _FB
    FLOOD = FLOOD + (_FB,)
except ImportError:
    pass

# ---------------- API (kodei rakha, env lagbe na) ----------------
API_ID = 37109385
API_HASH = "b50a9ccaf4a0352b895a9fb2998c7f0d"
SESSION = ""  # chaile ekhane main session string boshao, na hole website e paste koro
PORT = int(os.environ.get("PORT", 10000))  # host nije dey

CONFIG_FILE = os.path.join(DATA, "config.json")
SESSION_FILE = os.path.join(DATA, "session.txt")
LOG_FILE = os.path.join(DATA, "logs.json")
WARN_FILE = os.path.join(DATA, "warns.json")
REACT_FILE = os.path.join(DATA, "done_react.json")
CAPTCHA_FILE = os.path.join(DATA, "captcha.json")
STRIKE_FILE = os.path.join(DATA, "strikes.json")
JOINED_FILE = os.path.join(DATA, "joined.json")
LOCKS_FILE = os.path.join(DATA, "locks.json")
BLACKLIST_FILE = os.path.join(DATA, "blacklist.json")
STATS_FILE = os.path.join(DATA, "stats.json")
TEMPLATES_FILE = os.path.join(DATA, "templates.json")

# Telegram reaction hishebe je emoji gulo allowed (standard list)
ALLOWED_REACTIONS = (
    "👍 👎 ❤ 🔥 🥰 👏 😁 🤔 🤯 😱 🤬 😢 🎉 🤩 🤮 💩 🙏 👌 🕊 🤡 🥱 🥴 😍 🐳 🌚 🌭 💯 🤣 ⚡ 🍌 🏆 "
    "💔 🤨 😐 🍓 🍾 💋 🖕 😈 😴 😭 🤓 👻 👀 🎃 🙈 😇 😨 🤝 ✍ 🤗 🫡 🎅 🎄 ☃ 💅 🤪 🗿 🆒 💘 🙉 🦄 😘 "
    "💊 🙊 😎 👾 🤷 😡"
).split()

DEFAULT_RIGHTS = {
    "delete_messages": True, "ban_users": True, "invite_users": True, "pin_messages": True,
    "change_info": False, "add_admins": False, "manage_call": False, "anonymous": False,
}

DEFAULT_SETTINGS = {
    "dry_run": False,          # true hole kono kaj hobe na, shudhu log e likhbe
    "confirm_all": False,      # sob action e confirm chaibe
    "undo_seconds": 5,         # react dewar pore koto sec er moddhe sariye nile bondho hobe (0 = off)
    "max_actions_per_min": 20,
    "prefix": ".",
    "delete_command": True,
    "react_max_age_h": 72,     # eta cheye purano message e react e kaj hobe na (0 = off)
    "warn_limit": 3,
    "warn_action": "mute",     # mute | ban | kick
    "warn_mute_min": 1440,
    "notify_in_chat": False,
    "bot_token": "",
    "cas_check": False,        # notun member ke CAS (Combot Anti-Spam) list e dekhe, spammer hole ban
    "log_chat": "",            # sob action er log ei group/channel e pathabe (id ba @username)
    # ---------------- LINK SHIELD (notun) ----------------
    "link_guard": True,             # MASTER SWITCH: jekono group e link dile sathe sathe delete
    "link_all_admin_groups": True,  # je je group e ami admin sei sob group e apna apni chalu
    "link_notice": True,            # group e chhoto warning pathabe (nijei muchhe jabe)
    "link_notice_s": 12,            # oi warning koto sec pore muchbe
    "link_bot_fallback": True,      # main account fail korle bot diye delete korbe
    "auto_blacklist": True,         # bar bar link dile auto blacklist (tar sob message delete)
    "auto_blacklist_after": 3,      # koybar link dile blacklist hobe
    "link_block_edit": True,        # message edit kore link bosalo-o dhora porbe
    "link_block_buttons": True,     # inline URL button wala message o delete
    "delete_join_left": False,      # join/leave er service message sob group e muchbe
    "reply_delete_s": 0,            # command er uttor koto sec pore muchbe (0 = na)
}


def _r(rid, name, trigger, actions, enabled=True, who="me", confirm=False):
    return {"id": rid, "name": name, "enabled": enabled, "trigger": trigger, "who": who,
            "groups": ["*"], "confirm": confirm, "actions": actions}


DEFAULT_RULES = [
    _r("r_ban", "Ban (react)", {"type": "reaction", "emoji": "🤬"},
       [{"type": "ban", "duration_min": 0, "delete_history": False}]),
    _r("r_mute", "Mute 1 ghonta (react)", {"type": "reaction", "emoji": "🤡"},
       [{"type": "mute", "duration_min": 60}]),
    _r("r_del", "Message delete (react)", {"type": "reaction", "emoji": "💩"},
       [{"type": "delete"}]),
    _r("r_warn", "Warn (react)", {"type": "reaction", "emoji": "👀"},
       [{"type": "warn"}]),
    _r("r_admin", "Admin banao (react)", {"type": "reaction", "emoji": "🏆"},
       [{"type": "promote", "title": "Moderator", "rights": dict(DEFAULT_RIGHTS)}], enabled=False),
    _r("c_ban", "Command .ban", {"type": "command", "name": "ban"},
       [{"type": "ban", "duration_min": 0, "delete_history": False}]),
    _r("c_mute", "Command .mute 30m", {"type": "command", "name": "mute"},
       [{"type": "mute", "duration_min": 60}]),
    _r("c_unban", "Command .unban", {"type": "command", "name": "unban"}, [{"type": "unban"}]),
    _r("c_unmute", "Command .unmute", {"type": "command", "name": "unmute"}, [{"type": "unmute"}]),
    _r("c_kick", "Command .kick", {"type": "command", "name": "kick"}, [{"type": "kick"}]),
    _r("c_warn", "Command .warn", {"type": "command", "name": "warn"}, [{"type": "warn"}]),
    _r("c_unwarn", "Command .unwarn", {"type": "command", "name": "unwarn"}, [{"type": "unwarn"}]),
    _r("c_del", "Command .del", {"type": "command", "name": "del"}, [{"type": "delete"}]),
    _r("c_delall", "Command .delall (sob message)", {"type": "command", "name": "delall"},
       [{"type": "delete_all"}]),
    _r("c_promote", "Command .promote", {"type": "command", "name": "promote"},
       [{"type": "promote", "title": "", "rights": dict(DEFAULT_RIGHTS)}]),
    _r("c_demote", "Command .demote", {"type": "command", "name": "demote"}, [{"type": "demote"}]),
    _r("c_pin", "Command .pin", {"type": "command", "name": "pin"}, [{"type": "pin"}]),
    _r("c_restrict", "Command .restrict 1h (shudhu dekhte parbe)", {"type": "command", "name": "restrict"},
       [{"type": "restrict", "duration_min": 60, "perms": {}}]),
    _r("c_purge", "Command .purge (reply kora message theke shesh porjonto muche)", {"type": "command", "name": "purge"},
       [{"type": "purge"}]),
    _r("c_lock", "Command .lock 30m (group lock)", {"type": "command", "name": "lock"},
       [{"type": "lock", "duration_min": 0, "perms": {}}]),
    _r("c_unlock", "Command .unlock", {"type": "command", "name": "unlock"}, [{"type": "unlock"}]),
    _r("c_slow", "Command .slow 30 (second)", {"type": "command", "name": "slow"},
       [{"type": "slowmode", "seconds": 30}]),
    _r("c_gban", "Command .gban (sob group theke ban)", {"type": "command", "name": "gban"}, [{"type": "gban"}]),
    _r("c_ungban", "Command .ungban", {"type": "command", "name": "ungban"}, [{"type": "ungban"}]),
]

LOCK_NAMES = ["links", "mention", "hashtag", "email", "phone", "long", "emoji", "inline_buttons", "via_bot",
              "forward", "photo", "video", "sticker", "gif", "voice", "video_note", "audio", "document",
              "poll", "contact", "location", "game"]

DEFAULT_LINK_GUARD = {
    "on": True,                    # ei group e link shield chalu
    "exempt_admins": True,         # group er admin ra link dite parbe
    "mode": "strike",              # delete | warn | strike | mute | ban | kick
    "mute_min": 120,               # mute/restrict hole koto minit
    "ban_after": 3,                # koybar link dile direct ban (0 = na)
    "steps": [{"action": "warn", "mute_min": 0},
              {"action": "mute", "mute_min": 120},
              {"action": "ban", "mute_min": 0}],
    "notice": "🚫 {name}, ei group e link pathano nishiddho! Link sathe sathe delete hoye giyeche. ({n}/{max})",
    "notice_s": 12,                # notice koto sec pore muchbe
    "allow": [],                   # ei domain gulor link thakle delete hobe na (ek line e ekta)
    "block_buttons": True,         # inline URL button wala message
    "block_edits": True,           # edit kore link bosaleo dhora porbe
    "block_forward": True,         # forward kora message e link thakleo delete
    "block_names": True,           # username/name er moddhe link (jemon "join t.me/x")
}

DEFAULT_GROUP = {
    "enabled": True,
    "rules_text": "",
    "filters": [],     # [{"key": "price", "reply": "..."}]  keyword likhle auto reply
    "link_guard": dict(DEFAULT_LINK_GUARD),
    "automod": {
        "enabled": False,
        # prottek lock: action = delete (shudhu muche) | strike (dhap dhap shasti) | mute | ban
        "locks": {n: {"on": False, "action": "strike", "mute_min": 60} for n in LOCK_NAMES},
        "links_allow": [],           # ei domain/link thakle block hobe na
        "long_max": 1500,
        "emoji_max": 12,
        "words": {"on": False, "list": [], "action": "strike", "mute_min": 60},   # "re:" diye likhle regex
        "flood": {"on": False, "count": 6, "seconds": 8, "action": "mute", "mute_min": 10},
        "newbie": {"on": False, "hours": 24, "block": ["links", "media"]},
        # 1st bar = warn (shudhu hushiyar), 2nd bar = mute (group e thakbe), ...
        "strikes": {
            "window_h": 24,
            "steps": [{"action": "warn", "mute_min": 0}, {"action": "mute", "mute_min": 60}],
            "warn_text": "⚠ {name}, ekhane {kind} deya jabe na. ({n}/{max})",
            "notify_delete_s": 15,
        },
    },
    "antibot": {"on": False, "mode": "non_admin", "punish": "none"},   # mode: non_admin | everyone
    "antiraid": {"on": False, "joins": 10, "seconds": 30, "lock_min": 10},
    "night": {"on": False, "from": "23:00", "to": "06:00", "tz": 360},
    "clean": {"join": False, "leave": False, "pin": False},
    "welcome": {"on": False, "text": "Swagotom {name}! 🎉", "delete_after": 60},
    "captcha": {"on": False, "timeout_min": 5, "fail": "kick",
                "text": "{name}, niche click kore prove koro tumi manush"},
}


def jload(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def jsave(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def deep_merge(base, over):
    out = json.loads(json.dumps(base))
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def norm_emoji(e):
    return (e or "").replace("\ufe0f", "").replace("\u200d", "").strip()


def flood_secs(e):
    try:
        return max(1, int(getattr(e, "seconds", 5)))
    except Exception:
        return 5


def parse_duration(tok):
    """'30m' '2h' '1d' '45' (minit) -> minit. Bujhte na parle None."""
    m = re.fullmatch(r"(\d+)\s*([smhdw]?)", (tok or "").strip().lower())
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2) or "m"
    mult = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440, "w": 10080}[u]
    return max(1, int(round(n * mult)))


def display_name(u):
    if u is None:
        return "?"
    t = getattr(u, "title", None)
    if t:
        return t
    n = ((getattr(u, "first_name", "") or "") + " " + (getattr(u, "last_name", "") or "")).strip()
    un = getattr(u, "username", None)
    if n:
        return n
    return f"@{un}" if un else str(getattr(u, "id", "?"))


class Hub:
    def __init__(self):
        self.client = None
        self.bot = None
        self.me = None
        self.me_id = 0
        self.me_name = ""
        self.status = "need_session"   # need_session | connecting | ready
        self.error = ""
        self.bot_status = ""
        self.started = time.time()
        self.plugins = []
        self.pending = {}              # confirm waiting
        self.logs = deque(jload(LOG_FILE, [])[:500], maxlen=500)
        self.names = {}
        self.admin_cache = {}
        self.groups_cache = ([], 0)
        self.react_state = {}
        self.react_debug = deque(maxlen=30)
        self.done_react = set(jload(REACT_FILE, []))
        self.warns = jload(WARN_FILE, {})
        self.captcha = jload(CAPTCHA_FILE, {})
        self.strikes = jload(STRIKE_FILE, {})
        self.joined = jload(JOINED_FILE, {})
        self.locks = jload(LOCKS_FILE, {})     # chat -> {"until": ts, "prev": {...}, "by": "raid|night|manual"}
        self.blacklist = jload(BLACKLIST_FILE, {})   # uid(str) -> {"name":..., "reason":..., "t":..., "count":...}
        self.stats = self._load_stats()
        self.right_cache = {}                  # (chat, right) -> (ts, bool)
        self._gcache = {}                      # group config cache
        self.raid_joins = {}
        self.night_state = {}
        self.action_times = deque()
        self.cfg = self._load_cfg()

    # ---------- config ----------
    def _load_cfg(self):
        saved = jload(CONFIG_FILE, {})
        cfg = {
            "settings": deep_merge(DEFAULT_SETTINGS, saved.get("settings")),
            "rules": saved.get("rules") if isinstance(saved.get("rules"), list) else json.loads(json.dumps(DEFAULT_RULES)),
            "trusted": saved.get("trusted") or [],
            "protected": saved.get("protected") or [],
            "groups": saved.get("groups") or {},
            "gban": saved.get("gban") or [],
        }
        return cfg

    def save(self):
        jsave(CONFIG_FILE, self.cfg)
        self._gcache = {}

    def group_cfg(self, chat_id):
        key = str(chat_id)
        c = self._gcache.get(key)
        if c is None:
            c = deep_merge(DEFAULT_GROUP, self.cfg["groups"].get(key))
            if len(self._gcache) > 400:
                self._gcache.clear()
            self._gcache[key] = c
        return c

    # ---------- log ----------
    def log(self, **kw):
        e = {"id": uuid.uuid4().hex[:8], "t": time.time(), **kw}
        self.logs.appendleft(e)
        try:
            jsave(LOG_FILE, list(self.logs))
        except Exception:
            pass
        print(f"[{e.get('kind','log')}] {e.get('msg','')}", flush=True)
        if e.get("kind") == "action" and self.client and str(self.cfg["settings"].get("log_chat") or "").strip():
            try:
                asyncio.get_running_loop().create_task(self._mirror(e))
            except RuntimeError:
                pass
        return e

    async def _mirror(self, e):
        ref = str(self.cfg["settings"]["log_chat"]).strip()
        try:
            ref = int(ref)
        except ValueError:
            pass
        text = (f"{'✅' if e.get('ok', True) else '❌'} {e.get('chat_title', '')}\n"
                f"{e.get('user_name', '')}: {e.get('msg', '')}\n({e.get('rule', '')})")
        try:
            await self.client.send_message(ref, text)
        except Exception:
            pass

    def rate_ok(self):
        now = time.time()
        q = self.action_times
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= int(self.cfg["settings"].get("max_actions_per_min", 20)):
            return False
        q.append(now)
        return True

    # ---------- warns / reactions / captcha store ----------
    def warn_get(self, chat, user):
        return int(self.warns.get(f"{chat}:{user}", 0))

    def warn_add(self, chat, user, n=1):
        k = f"{chat}:{user}"
        self.warns[k] = max(0, int(self.warns.get(k, 0)) + n)
        if self.warns[k] == 0:
            self.warns.pop(k, None)
        jsave(WARN_FILE, self.warns)
        return self.warns.get(k, 0)

    def warn_reset(self, chat, user):
        self.warns.pop(f"{chat}:{user}", None)
        jsave(WARN_FILE, self.warns)

    def strike_add(self, chat, user, window_h):
        """Notun dhap gune ekhon koto nombor dhap ta ferot dey (purano gulo window er baire gele bad)"""
        k, now = f"{chat}:{user}", time.time()
        lst = [t for t in self.strikes.get(k, []) if now - t < max(1, window_h) * 3600]
        lst.append(now)
        self.strikes[k] = lst
        jsave(STRIKE_FILE, self.strikes)
        return len(lst)

    def mark_joined(self, chat, user):
        now = time.time()
        self.joined[f"{chat}:{user}"] = now
        if len(self.joined) > 3000:
            self.joined = {k: t for k, t in self.joined.items() if now - t < 7 * 86400}
        jsave(JOINED_FILE, self.joined)

    def joined_hours_ago(self, chat, user):
        t = self.joined.get(f"{chat}:{user}")
        return None if t is None else (time.time() - t) / 3600

    def gban_ids(self):
        out = set()
        for g in self.cfg["gban"]:
            try:
                out.add(int(g["id"]))
            except Exception:
                pass
        return out

    def save_locks(self):
        jsave(LOCKS_FILE, self.locks)

    # ---------- blacklist ----------
    def blacklisted(self, uid):
        return str(uid) in self.blacklist

    def blacklist_add(self, uid, name="", reason=""):
        k = str(uid)
        rec = self.blacklist.get(k) or {}
        rec.update({"name": name or rec.get("name", ""), "reason": reason or rec.get("reason", ""),
                    "t": time.time(), "count": int(rec.get("count", 0)) + 1})
        self.blacklist[k] = rec
        try:
            jsave(BLACKLIST_FILE, self.blacklist)
        except Exception:
            pass
        return rec

    def blacklist_del(self, uid):
        self.blacklist.pop(str(uid), None)
        try:
            jsave(BLACKLIST_FILE, self.blacklist)
        except Exception:
            pass

    def save_blacklist(self):
        try:
            jsave(BLACKLIST_FILE, self.blacklist)
        except Exception:
            pass

    # ---------- stats ----------
    def _load_stats(self):
        st = jload(STATS_FILE, {}) or {}
        st.setdefault("day", "")
        st.setdefault("today", {})
        st.setdefault("history", {})
        st.setdefault("offenders", {})
        st.setdefault("groups", {})
        st.setdefault("total", {})
        self._roll_stats(st)
        return st

    @staticmethod
    def _today():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _roll_stats(self, st=None):
        st = st if st is not None else self.stats
        if st.get("day") != self._today():
            old = st.get("day") or ""
            if old and st.get("today"):
                st.setdefault("history", {})[old] = st["today"]
            hist = st.get("history") or {}
            if len(hist) > 30:
                for k in sorted(hist)[:-30]:
                    hist.pop(k, None)
            st["history"] = hist
            st["today"] = {}
            st["day"] = self._today()
        st.setdefault("today", {})
        return st

    def bump(self, chat=None, chat_title="", user=None, user_name="", **counters):
        """Stat gonoi (link delete, warn, mute, ban ...)."""
        try:
            st = self._roll_stats()
            for k, v in counters.items():
                if not v:
                    continue
                st["today"][k] = int(st["today"].get(k, 0)) + int(v)
                st["total"][k] = int(st["total"].get(k, 0)) + int(v)
            if user:
                off = st.setdefault("offenders", {})
                o = off.get(str(user)) or {"n": 0, "name": "", "last": 0, "chat": chat}
                o["n"] = int(o.get("n", 0)) + 1
                o["name"] = user_name or o.get("name") or str(user)
                o["last"] = time.time()
                o["chat"] = chat or o.get("chat")
                off[str(user)] = o
                if len(off) > 1500:
                    for k in sorted(off, key=lambda x: off[x].get("last", 0))[:500]:
                        off.pop(k, None)
            if chat:
                g = st.setdefault("groups", {})
                r = g.get(str(chat)) or {"n": 0, "title": ""}
                r["n"] = int(r.get("n", 0)) + 1
                if chat_title:
                    r["title"] = chat_title
                g[str(chat)] = r
            jsave(STATS_FILE, st)
        except Exception:
            pass

    def offender_count(self, uid):
        st = self._roll_stats()
        return int(((st.get("offenders") or {}).get(str(uid)) or {}).get("n", 0))

    def stats_public(self):
        st = self._roll_stats()
        hist = []
        for d in sorted(list((st.get("history") or {}).keys()) + [st["day"]])[-7:]:
            row = (st.get("history") or {}).get(d) or (st["today"] if d == st["day"] else {})
            hist.append({"day": d, "links": int(row.get("links", 0)), "actions": int(row.get("actions", 0))})
        offs = sorted(({"id": int(k), **v} for k, v in (st.get("offenders") or {}).items()),
                      key=lambda x: -int(x.get("n", 0)))[:15]
        grps = sorted(({"id": int(k), **v} for k, v in (st.get("groups") or {}).items()),
                      key=lambda x: -int(x.get("n", 0)))[:10]
        return {"today": st["today"], "total": st.get("total", {}), "history": hist,
                "offenders": offs, "groups": grps, "day": st["day"]}

    # ---------- message delete (retry + bot fallback) ----------
    async def delete_msgs(self, chat_id, ids, retries=1):
        ids = [i for i in (ids or []) if i]
        if not self.client or not ids:
            return False
        try:
            ent = await self.entity(chat_id)
        except Exception:
            ent = chat_id
        for attempt in range(retries + 1):
            try:
                await self.client.delete_messages(ent, ids, revoke=True)
                return True
            except FLOOD as e:
                await asyncio.sleep(min(flood_secs(e), 60) + 1)
            except Exception:
                if attempt >= retries:
                    break
                await asyncio.sleep(0.8)
        if self.cfg["settings"].get("link_bot_fallback", True) and self.bot:
            try:
                await self.bot.delete_messages(ent, ids)
                return True
            except Exception:
                pass
        return False

    async def can_delete(self, chat_id, force=False):
        """Ei group e message delete korar adhikar ache kina (10 min cache)"""
        key = (chat_id, "delete_messages")
        now = time.time()
        c = self.right_cache.get(key)
        if c and not force and now - c[0] < 600:
            return c[1]
        try:
            ent = await self.entity(chat_id)
            val = await self.has_right(ent, "delete_messages")
        except Exception:
            val = None
        val = bool(val)
        self.right_cache[key] = (now, val)
        return val

    def save_done_react(self):
        if len(self.done_react) > 5000:
            self.done_react = set(list(self.done_react)[-3000:])
        jsave(REACT_FILE, list(self.done_react))

    def save_captcha(self):
        jsave(CAPTCHA_FILE, self.captcha)

    # ---------- telegram helpers ----------
    async def entity(self, ref):
        try:
            return await self.client.get_entity(ref)
        except (ValueError, TypeError):
            await self.client.get_dialogs()
            return await self.client.get_entity(ref)

    async def user_name(self, uid):
        if uid in self.names:
            return self.names[uid]
        try:
            n = display_name(await self.entity(uid))
        except Exception:
            n = str(uid)
        self.names[uid] = n
        return n

    async def fill_names(self, ctx):
        if ctx.get("chat") is None:
            ctx.setdefault("chat_title", "")
        elif "chat_title" not in ctx:
            try:
                ctx["chat_title"] = display_name(await self.entity(ctx["chat"]))
            except Exception:
                ctx["chat_title"] = str(ctx["chat"])
        if ctx.get("user") and "user_name" not in ctx:
            ctx["user_name"] = await self.user_name(ctx["user"])
        ctx.setdefault("user_name", "")
        if ctx.get("by") and "by_name" not in ctx:
            ctx["by_name"] = await self.user_name(ctx["by"])
        ctx.setdefault("by_name", "")

    async def has_right(self, ent, right):
        """True/False; jani na hole None"""
        try:
            p = await self.client.get_permissions(ent, self.me_id)
        except Exception:
            return None
        if getattr(p, "is_creator", False):
            return True
        if not getattr(p, "is_admin", False):
            return False
        return bool(getattr(p, right, False))

    async def admin_ids(self, chat_id, force=False):
        now = time.time()
        c = self.admin_cache.get(chat_id)
        if c and not force and now - c[0] < 300:
            return c[1]
        ids = set()
        try:
            ent = await self.entity(chat_id)
            async for u in self.client.iter_participants(ent, filter=types.ChannelParticipantsAdmins):
                ids.add(u.id)
        except Exception:
            pass
        self.admin_cache[chat_id] = (now, ids)
        return ids

    async def is_protected(self, chat_id, user_id):
        if user_id == self.me_id or user_id in {int(x) for x in self.cfg["protected"]}:
            return True
        return user_id in await self.admin_ids(chat_id)

    def trusted_ids(self):
        return {int(t["id"]) for t in self.cfg["trusted"]}

    async def notify_owner(self, text, buttons=None):
        if self.bot and buttons:
            try:
                await self.bot.send_message(self.me_id, text, buttons=buttons)
                return True
            except Exception as e:
                self.log(kind="note", msg=f"Bot diye jaanano jayni (bot ke ekbar /start dao): {e}")
        try:
            await self.client.send_message("me", text + ("\n\n(Website e giye Confirm koro)" if buttons else ""))
        except Exception:
            pass
        return False

    # ---------- groups list ----------
    async def list_groups(self, force=False):
        items, t = self.groups_cache
        if items and not force and time.time() - t < 120:
            return items
        out = []
        async for d in self.client.iter_dialogs():
            if not d.is_group:
                continue
            e = d.entity
            creator = bool(getattr(e, "creator", False))
            ar = getattr(e, "admin_rights", None)

            def r(name):
                return creator or bool(ar and getattr(ar, name, False))
            out.append({
                "id": d.id, "title": d.name or str(d.id),
                "admin": creator or ar is not None,
                "creator": creator,
                "rights": {k: r(k) for k in ("ban_users", "delete_messages", "add_admins",
                                             "invite_users", "pin_messages", "change_info")},
                "members": getattr(e, "participants_count", None),
            })
        out.sort(key=lambda g: (not g["admin"], g["title"].lower()))
        self.groups_cache = (out, time.time())
        return out

    # ---------- plugins ----------
    def load_plugins(self):
        pdir = os.path.join(BASE, "plugins")
        if BASE not in sys.path:
            sys.path.insert(0, BASE)
        for fn in sorted(os.listdir(pdir)):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            try:
                self.plugins.append(importlib.import_module("plugins." + fn[:-3]))
            except Exception as e:
                self.log(kind="error", msg=f"Plugin {fn} load hoyni: {type(e).__name__}: {e}")

    def attach_user(self, client):
        for m in self.plugins:
            fn = getattr(m, "attach", None)
            if fn:
                try:
                    fn(self, client)
                except Exception as e:
                    self.log(kind="error", msg=f"{m.__name__}.attach: {e}")

    def attach_bot(self, bot):
        for m in self.plugins:
            fn = getattr(m, "attach_bot", None)
            if fn:
                try:
                    fn(self, bot)
                except Exception as e:
                    self.log(kind="error", msg=f"{m.__name__}.attach_bot: {e}")

    def start_background(self):
        for m in self.plugins:
            fn = getattr(m, "background", None)
            if fn:
                asyncio.create_task(fn(self))

    # ---------- connect ----------
    async def disconnect(self):
        for c in (self.client, self.bot):
            if c:
                try:
                    await c.disconnect()
                except Exception:
                    pass
        self.client = None
        self.bot = None
        self.groups_cache = ([], 0)
        self.admin_cache = {}

    async def connect(self, session):
        await self.disconnect()
        self.status, self.error = "connecting", ""
        try:
            c = TelegramClient(StringSession(session.strip()), API_ID, API_HASH, flood_sleep_threshold=20)
            await c.connect()
            if not await c.is_user_authorized():
                await c.disconnect()
                raise ValueError("Session valid na (logout hoye geche ba bhul string)")
            me = await c.get_me()
        except Exception as e:
            self.status, self.error = "need_session", str(e)
            self.log(kind="error", msg=f"Connect fail: {e}")
            return False
        self.client, self.me, self.me_id = c, me, me.id
        self.me_name = display_name(me)
        with open(SESSION_FILE, "w") as f:
            f.write(session.strip())
        self.status = "ready"
        self.attach_user(c)
        asyncio.create_task(self._warm())
        await self.connect_bot()
        self.log(kind="note", msg=f"Connected: {self.me_name}")
        return True

    async def _warm(self):
        try:
            await self.client.get_dialogs(limit=300)
        except Exception:
            pass

    async def connect_bot(self):
        if self.bot:
            try:
                await self.bot.disconnect()
            except Exception:
                pass
            self.bot = None
        tok = (self.cfg["settings"].get("bot_token") or "").strip()
        self.bot_status = ""
        if not tok:
            return
        try:
            b = TelegramClient(StringSession(), API_ID, API_HASH)
            await b.start(bot_token=tok)
            bme = await b.get_me()
            self.bot, self.bot_status = b, "@" + (bme.username or "bot")
            self.attach_bot(b)
        except Exception as e:
            self.bot, self.bot_status = None, f"Error: {str(e)[:100]}"
            self.log(kind="error", msg=f"Bot connect fail: {e}")

    async def logout(self):
        await self.disconnect()
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.status, self.me, self.me_id, self.me_name = "need_session", None, 0, ""


hub = Hub()
