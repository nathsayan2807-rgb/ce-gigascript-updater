CE Gigascript Auto-Patcher
==========================

What it does
------------
- Polls the upstream LL Gigascript every 15 minutes.
- Patches a local copy so gigascriptLayoutReady() always returns true.
- Serves the patched copy at http://127.0.0.1:8765/LL-Gigascript.user.js.
- If the upstream structure changes, it refuses to publish a new version and keeps
  serving the last known-good patched file.

Requirements
------------
Python 3.10+ and internet access.

First-time setup
----------------
1. Put ce_gigascript_auto_patcher.py in a permanent folder.
2. Run: python ce_gigascript_auto_patcher.py --once
3. Run: python ce_gigascript_auto_patcher.py --serve
4. In your userscript manager, install this URL:
   http://127.0.0.1:8765/LL-Gigascript.user.js
5. Keep the installed script's @updateURL and @downloadURL pointed at localhost.
6. Stop the foreground process with Ctrl+C, then run:
   python ce_gigascript_auto_patcher.py --install-startup
7. Start it now with --serve, or log out and back in.

Automation details
------------------
- The helper checks upstream immediately and then every 15 minutes.
- The userscript manager controls when it checks the local update URL; it may take
  longer than 15 minutes for the browser copy to refresh.
- Status endpoint: http://127.0.0.1:8765/health
- Logs/state: ~/.ce-gigascript-auto-patcher/ (Windows resolves this under your home).
- The server binds only to 127.0.0.1.
- This modifies only a local copy, not the upstream source.
- The patcher cannot click through userscript-manager install dialogs.
- If the manager refuses localhost update URLs, it needs to permit local HTTP update
  URLs or the hosting approach must be changed.
