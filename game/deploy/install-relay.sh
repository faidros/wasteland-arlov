#!/usr/bin/env bash
# Install the arena relay on an Ubuntu server (run as root ON THE SERVER; deploy-arena.sh does this for you).
#   ARENA_DOMAIN=arena.example.com CERT_EMAIL=you@example.com ALLOWED_ORIGINS=https://example.com bash deploy/install-relay.sh
# The relay only forwards messages between browsers: no city, physics or game state lives on the server.
# It listens on 127.0.0.1:5221 behind nginx — or behind Caddy when the server already runs Caddy;
# only ports 80/443 are public. An existing Node installation is reused.
set -euo pipefail
umask 022

: "${ARENA_DOMAIN:?Set ARENA_DOMAIN, e.g. arena.example.com}"
: "${CERT_EMAIL:?Set CERT_EMAIL for Let's Encrypt notices}"
: "${ALLOWED_ORIGINS:?Set ALLOWED_ORIGINS to the web address(es) that host the game, comma separated, e.g. https://example.com}"
[[ $(uname -s) == Linux && $(id -u) == 0 ]] || { echo 'Run on the Ubuntu relay server as root.' >&2; exit 1; }
bundle_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for file in server/index.mjs server/package.json server/package-lock.json deploy/wasteland-arena.service deploy/nginx-arena.conf deploy/caddy-arena.caddy; do
  [[ -f "$bundle_root/$file" ]] || { echo "Missing bundle file: $file" >&2; exit 1; }
done

# Web server: reuse Caddy if it already serves 80/443 (it then handles TLS); otherwise nginx + Certbot.
mode=nginx
if systemctl is-active --quiet caddy 2>/dev/null; then
  mode=caddy
elif ! command -v nginx >/dev/null; then
  listeners="$(ss -H -ltnp '( sport = :80 or sport = :443 )')"
  [[ -z "$listeners" ]] || { echo "Another web server already uses port 80/443 (not nginx or Caddy):" >&2; echo "$listeners" >&2; echo 'Inspect it before installing.' >&2; exit 1; }
fi
echo "Web server mode: $mode"

packages=()
# Reuse an existing Node (wherever it lives) and its npm; only install them when missing.
node_bin="$(command -v node || true)"
npm_bin="$(command -v npm || true)"
if [[ -n "$node_bin" && -z "$npm_bin" && -x "$(dirname "$(readlink -f "$node_bin")")/npm" ]]; then
  npm_bin="$(dirname "$(readlink -f "$node_bin")")/npm"
fi
if [[ -z "$node_bin" ]]; then
  packages+=(nodejs npm)
elif [[ -z "$npm_bin" ]]; then
  echo "Node is installed at $node_bin but its npm was not found. Install npm for that Node first (the apt npm package may bring a second Node)." >&2
  exit 1
fi
command -v curl >/dev/null || packages+=(curl)
if [[ $mode == nginx ]]; then
  command -v nginx >/dev/null || packages+=(nginx)
  if ! command -v certbot >/dev/null; then
    packages+=(certbot python3-certbot-nginx)
  elif ! certbot plugins 2>/dev/null | grep -q 'nginx'; then
    packages+=(python3-certbot-nginx)
  fi
fi
if ((${#packages[@]})); then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"
fi
node_bin="$(command -v node)"
npm_bin="${npm_bin:-$(command -v npm)}"
"$node_bin" -e 'if(Number(process.versions.node.split(".")[0])<18)throw Error("Node 18+ is required; update it separately after reviewing other services on this server.")'

id -u wasteland-arena >/dev/null 2>&1 || useradd --system --user-group --home-dir /nonexistent --shell /usr/sbin/nologin wasteland-arena
install -d -o wasteland-arena -g wasteland-arena -m 0755 /opt/wasteland-arena
for file in index.mjs package.json package-lock.json; do
  install -o wasteland-arena -g wasteland-arena -m 0644 "$bundle_root/server/$file" "/opt/wasteland-arena/$file"
done
runuser -u wasteland-arena -- env PATH="$(dirname "$node_bin"):$PATH" "$npm_bin" ci --omit=dev --ignore-scripts --cache /opt/wasteland-arena/.npm --prefix /opt/wasteland-arena
service=/etc/systemd/system/wasteland-arena.service
[[ ! -f "$service" ]] || cp -p "$service" "$service.backup-$(date +%Y%m%d-%H%M%S)"
sed -e "s|ExecStart=/usr/bin/node |ExecStart=$node_bin |" -e "s|__ALLOWED_ORIGINS__|${ALLOWED_ORIGINS}|" \
  "$bundle_root/deploy/wasteland-arena.service" > "$service"
chmod 0644 "$service"
systemctl daemon-reload
systemctl enable wasteland-arena.service
systemctl restart wasteland-arena.service
for attempt in {1..20}; do
  if curl -fsS http://127.0.0.1:5221/health > /tmp/wasteland-arena-health.json; then break; fi
  sleep .25
done
"$node_bin" -e 'const h=JSON.parse(require("node:fs").readFileSync("/tmp/wasteland-arena-health.json"));if(!h.ok||h.mode!=="relay")throw Error("Relay health check failed");console.log(h)'

if [[ $mode == caddy ]]; then
  caddyfile=/etc/caddy/Caddyfile
  if grep -qE "^${ARENA_DOMAIN//./\\.}[[:space:]]*\\{" "$caddyfile"; then
    echo "Caddyfile already has a block for $ARENA_DOMAIN — leaving it as it is."
  else
    cp -p "$caddyfile" "$caddyfile.backup-$(date +%Y%m%d-%H%M%S)"
    { echo; sed "s|__ARENA_DOMAIN__|${ARENA_DOMAIN}|" "$bundle_root/deploy/caddy-arena.caddy"; } >> "$caddyfile"
  fi
  caddy validate --config "$caddyfile" --adapter caddyfile
  systemctl reload caddy
else
  available=/etc/nginx/sites-available/wasteland-arena
  enabled=/etc/nginx/sites-enabled/wasteland-arena
  sed "s|__ARENA_DOMAIN__|${ARENA_DOMAIN}|" "$bundle_root/deploy/nginx-arena.conf" > "$available.new"
  if [[ -f "$available" ]] && grep -q 'managed by Certbot' "$available"; then
    rm "$available.new"  # keep the certificate-enabled vhost Certbot already rewrote
  else
    mv "$available.new" "$available"
  fi
  if [[ -e "$enabled" || -L "$enabled" ]]; then
    [[ $(readlink -f "$enabled") == "$available" ]] || { echo 'An existing wasteland-arena vhost needs review.' >&2; exit 1; }
  else
    ln -s "$available" "$enabled"
  fi
  nginx -t
  systemctl reload nginx
fi
if command -v ufw >/dev/null && ufw status | grep -q '^Status: active'; then
  ufw allow 80/tcp
  ufw allow 443/tcp
fi
public_ip="$(curl -fsS -4 https://api.ipify.org || true)"
resolved="$(getent ahostsv4 "$ARENA_DOMAIN" | awk '{print $1}' | sort -u | tr '\n' ' ')"
if [[ -z "$resolved" || ( -n "$public_ip" && " $resolved " != *" $public_ip "* ) ]]; then
  echo "Relay installed, but $ARENA_DOMAIN resolves to '${resolved:-nothing}' instead of this server (${public_ip:-unknown})." >&2
  echo 'Create the DNS A record, wait for it to propagate, then rerun this installer to get the HTTPS certificate.' >&2
  exit 2
fi
if [[ $mode == nginx ]]; then
  certbot --nginx -d "$ARENA_DOMAIN" --non-interactive --agree-tos --email "$CERT_EMAIL" --no-eff-email --redirect --keep-until-expiring
  nginx -t
  systemctl reload nginx
else
  echo 'Caddy requests and renews the certificate by itself once DNS points here.'
fi
echo "Ready: wss://${ARENA_DOMAIN}/ws (room relay only). Build the game with ARENA_URL=wss://${ARENA_DOMAIN}/ws"
