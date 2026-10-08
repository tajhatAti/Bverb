GROUP MODERATOR PRO (v2)
=======================

KIVABE CHALU KORBE
------------------
1. Shob file CodeNest e upload koro (main.py main file).
2. Job er link kholo -> Status tab e session string paste kore Connect.
3. Setai hobe. Groups tab theke group er "Chalu" tick, ar Settings e jao.

LINK SHIELD (notun, sobar theke boro kaj)
-----------------------------------------
Kono group e keu JEKONO PROKAR LINK dilei message ta sathe sathe delete hobe:
  - https://... , www.... , t.me/... , wa.me/... , chat.whatsapp.com/... , tg://...
  - "google[.]com", "google (dot) com", "google . com" (space diye bhanga link)
  - zero-width character diye lukaono link, "hxxp://" style link
  - inline URL button wala message
  - chhobi/video er caption e dewa link
  - edit kore pore link boshaleo dhora porbe
  - forward kora message e link thakleo delete
  - media/file name (photo.jpg, video.mp4) ke link bhabe delete korbe na

Default: Link Shield SOB group e CHALU (jodi oi group e delete korar adhikar thake).
Admin der link dite deoa jay (group settings e off kora jay).

Ki hobe (per group "mode"):
  delete  = shudhu delete
  warn    = delete + warn
  strike  = dhap dhap (1st warn, 2nd mute, 3rd ban) [default]
  mute / kick / ban = delete + sathe sathe shasti

Bar bar link dile (default 3 bar) user auto blacklist e jay ->
tokhon theke tar SOB message delete hobe.

UI (website) er tab gulo
------------------------
Dashboard    : stats, ek click er kaj (sob group e link ban chalu/bondho, lock/unlock),
               7 diner graph, top offender der ek click e blacklist.
Groups       : group khujo, instant toggle (Link Ban / AutoMod / Welcome / Anti-Bot),
               pura settings form, Members list + mute/ban/blacklist.
Link Shield  : master switch, warning text/sec, auto blacklist, per-group mode,
               ar "Link Tester" - text boshiye dekho link dhora porbe kina.
Rules        : react / command diye nijer rule banai (ban, mute, mute 30m, promote...).
People       : trusted moderator, blacklist, link offender, global ban, surokkhito list.
Log          : sob kaj er log + Undo button.
Settings     : dry-run, confirm, warn, bot token, broadcast, backup/restore.

BOT DIYE COMMAND (group e likho)
--------------------------------
.ban .mute 30m .unmute .kick .warn .unwarn .del .delall .purge 50 .pin
.lock .unlock .slow 30 .promote .demote .gban .ungban .restrict 1h
.shield on|off        -> Link Shield chalu/bondho (ei group e)
.shield               -> kothay kothay chalu dekhabe
.linktest <text>      -> text e link ache kina dekho
.wl youtube.com       -> ei domain er link delete hobe na
.unwl youtube.com
.bl / .unbl           -> (reply diye) blacklist / blacklist theke tule nao
.id .stats .help .rules

NOTE
----
Dhap dhap shasti: prothom bar hushiyar, ditio bar mute (group e thakbe).
Settings e Dry-run tick dile kichu delete hobe na, shudhu Log e dekhabe - test er jonno.
Backup/Restore Settings tab e.
