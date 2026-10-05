---
name: deploy-arena
description: Put a generated city game online — build the static website and set up the small WebSocket relay server for Online Arena multiplayer on a VPS (Vultr, Hetzner, DigitalOcean or any Ubuntu server) with nginx and a Let's Encrypt certificate, over the user's existing SSH keys. Use when the user wants to publish the game, play online with friends, "sätt upp en server på Vultr", set up multiplayer, or check/repair the arena server.
---

# Publish the game and run the arena relay

Read `game/deploy/README.md` first; it is the user-facing version of this procedure.

Architecture: the game is static files. Online Arena needs a relay that only forwards messages between
browsers in a room (no physics, no city data on the server). The relay listens on 127.0.0.1:5221
behind an nginx vhost with HTTPS → `wss://<arena domain>/ws`.

## Collect (ask the user)

- **Website**: where the game will be hosted and its origin(s), e.g. `https://example.com`
  (any static host: their web hotel, GitHub Pages, Netlify …).
- **Server**: IP of an Ubuntu 22.04+ VPS they control and the SSH user (usually `root`). If they have
  none: guide them through creating the smallest Vultr Cloud Compute instance (Ubuntu LTS, add their
  SSH public key) in the Vultr web console — they click, you explain. Do not create accounts or enter
  payment details.
- **Domain** for the relay, e.g. `arena.example.com`, and an e-mail for Let's Encrypt.

## Steps

1. **SSH check** (read-only): `ssh -o BatchMode=yes root@<ip> 'uname -a; cat /etc/os-release; ss -ltnp; systemctl list-units --type=service --state=running | head -40; ls /etc/nginx/sites-enabled 2>/dev/null'`.
   Use the user's existing keys; never read, print or copy private key files. If SSH fails, report the
   exact error (timeout = firewall/IP, `Permission denied (publickey)` = key not on the server).
   Note other services. The installer reuses Caddy when it already serves 80/443 (it appends one
   site block, with a backup, and Caddy handles TLS), otherwise uses nginx + Certbot, and stops if
   some other web server owns 80/443. An existing Node and its npm are reused.
2. **DNS**: an A record `<arena domain> → <ip>`. The user adds it at their DNS provider (or you do it
   in their already-open DNS panel with explicit permission). Check with `dig +short <domain>`.
3. **Install** from the `game/` folder (asks nothing interactively; safe to rerun):
   ```sh
   ARENA_DOMAIN=<domain> CERT_EMAIL=<email> ALLOWED_ORIGINS=<https://site[,https://www.site]> \
     ./deploy/deploy-arena.sh root@<ip>
   ```
   Show the user the command before running it (it changes their server). Exit code 2 = DNS not
   visible yet: wait and rerun to obtain the certificate.
4. **Verify**: `curl https://<domain>/health` → `{"ok":true,"mode":"relay"…}`; on the server
   `systemctl status wasteland-arena --no-pager`.
5. **Build the website** with the relay address and hand it over:
   ```sh
   python3 wasteland.py publish <slug> --arena wss://<domain>/ws
   ```
   Upload the contents of `game/dist/` (incl. `.htaccess` and `city/`) — the user does this, or you do
   it with their explicit go-ahead and their existing credentials.
6. **Test online**: open the published site in two browser windows (or two devices), choose ONLINE
   ARENA with the same room code; check that both cars move, shots hit, respawn works and
   disconnecting one window removes its car.

## Troubleshooting

- 403 on the WebSocket: the page's origin is missing from `ALLOWED_ORIGINS` — rerun the installer
  with the exact origin (scheme + host, no path).
- `wss` fails but `/health` works over http: the certificate step has not run (DNS) — rerun step 3.
  With Caddy, `journalctl -u caddy` shows the certificate attempts.
- Logs: `journalctl -u wasteland-arena -f`. Restart: `systemctl restart wasteland-arena`.
- The relay is for friends' games (no anti-cheat). Limits: 8 drivers per room, 20 rooms.
