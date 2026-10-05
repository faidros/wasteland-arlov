# Publishing the game and the online arena

The game is a static website. Online Arena additionally needs a tiny WebSocket **relay**: it only
forwards messages between browsers in the same room (max 8 drivers per room, 20 rooms). Physics,
weapons, damage and scores run in each browser, so a 1 GB / 1 vCPU VPS is plenty.

```
browser ──HTTPS──► your web host (game/dist/)          static files, ~20–60 MB per city
browser ──WSS────► arena.example.com/ws  (nginx) ─► 127.0.0.1:5221 relay (node, systemd)
```

## 1. Rent a small server (example: Vultr)

1. Create an account at vultr.com → **Deploy** → *Cloud Compute – Shared CPU*, any nearby region,
   **Ubuntu 24.04 LTS** (or newer), the smallest plan (1 vCPU / 1 GB is enough).
2. Under *SSH Keys* add your public key (`cat ~/.ssh/id_ed25519.pub`; create one with
   `ssh-keygen -t ed25519` if you have none). Never paste a private key anywhere.
3. Deploy and note the server's IPv4 address. Test: `ssh root@<ip>`.

Any Ubuntu VPS works the same way (Hetzner, DigitalOcean, Linode, a Raspberry Pi with a public IP …).

## 2. Point a domain at it

At your DNS provider create an **A record**, e.g. `arena.example.com → <server ip>` (TTL 600).
The arena must use HTTPS (`wss://`) because the game page is served over HTTPS; the installer gets a
free Let's Encrypt certificate once the name resolves to the server.

## 3. Install the relay

From the `game/` folder on your computer:

```sh
ARENA_DOMAIN=arena.example.com \
CERT_EMAIL=you@example.com \
ALLOWED_ORIGINS=https://example.com,https://www.example.com \
./deploy/deploy-arena.sh root@<server ip>
```

`ALLOWED_ORIGINS` are the web addresses that host the game (the browser's origin, no path). The
script uploads `server/` and `deploy/`, creates a `wasteland-arena` system user and service and
puts the relay behind the server's web server:

- **Caddy already running** (common on servers that host other things): a site block for your
  domain is appended to `/etc/caddy/Caddyfile` (backup first, `caddy validate`, reload). Caddy gets
  and renews the certificate itself. This is how the original Kalmar Wasteland relay runs on Vultr.
- **nginx, or nothing on 80/443**: a separate nginx vhost plus a Certbot certificate (nginx and
  Certbot are installed if missing).
- Anything else on 80/443: the script stops and shows what it found.

An existing Node (even outside `/usr/bin`, e.g. `/opt/node-*/bin`) and its npm are reused; Node is only
installed from apt when there is none. Other sites and services are never touched. If DNS has not
propagated yet it stops after the relay is running; just run it again later.

Check: `curl https://arena.example.com/health` → `{"ok":true,"mode":"relay",…}`.
On the server: `systemctl status wasteland-arena`, logs with `journalctl -u wasteland-arena -f`.
To update only the relay code later: rerun the script, or copy `server/index.mjs` to
`/opt/wasteland-arena/` (owner `wasteland-arena`) and `systemctl restart wasteland-arena`.

## 4. Build and upload the website

```sh
cd game
ARENA_URL=wss://arena.example.com/ws npm run build
```

Upload the **contents** of `game/dist/` (including `.htaccess` and the `city/` folder) to your web
host, in any sub-folder — all URLs are relative. Without `ARENA_URL` the site works fine, only the
Online Arena mode is unavailable.

To try the arena locally without a server: `npm run dev` already serves a relay at `/arena/ws`;
open the game in two browser windows, choose ONLINE ARENA and the same room code.

## Notes

- The relay trusts its players (friends' games): it verifies sender ids and rate-limits messages
  but has no anti-cheat. Keep the room code private if that matters.
- Ports: only 80/443 need to be open; the Node process listens on loopback.
- Remove it: `systemctl disable --now wasteland-arena`, then delete the nginx vhost
  (`/etc/nginx/sites-enabled/wasteland-arena`) or the Caddyfile block and reload the web server.
- Tested in production with the original game: foreign origins get 403, late joiners receive poses,
  hits are batched to stay below the relay's 150 messages/s limit (the flamethrower used to exceed it).
