#!/usr/bin/env bash
# Upload and install the arena relay on a fresh Ubuntu VPS (Vultr, Hetzner, DigitalOcean …) over SSH.
#
#   ARENA_DOMAIN=arena.example.com CERT_EMAIL=you@example.com ALLOWED_ORIGINS=https://example.com \
#     ./deploy/deploy-arena.sh root@203.0.113.10
#
# Uses your normal SSH keys/agent; nothing secret is read or copied. Safe to rerun (e.g. after DNS
# has propagated, to obtain the HTTPS certificate). See deploy/README.md.
set -euo pipefail
target="${1:?Usage: ARENA_DOMAIN=… CERT_EMAIL=… ALLOWED_ORIGINS=… $0 root@<server-ip>}"
: "${ARENA_DOMAIN:?Set ARENA_DOMAIN}" "${CERT_EMAIL:?Set CERT_EMAIL}" "${ALLOWED_ORIGINS:?Set ALLOWED_ORIGINS}"
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
bundle="$(mktemp -t wasteland-arena.XXXXXX).tgz"
tar -czf "$bundle" -C "$here" server/index.mjs server/package.json server/package-lock.json \
  deploy/install-relay.sh deploy/wasteland-arena.service deploy/nginx-arena.conf deploy/caddy-arena.caddy
echo "Checking SSH access to $target …"
ssh -o BatchMode=yes -o ConnectTimeout=15 "$target" 'uname -sr; . /etc/os-release && echo "$PRETTY_NAME"'
remote_dir="/tmp/wasteland-arena-$(date +%s)"
ssh "$target" "mkdir -p $remote_dir"
scp -q "$bundle" "$target:$remote_dir/bundle.tgz"
ssh "$target" "cd $remote_dir && tar -xzf bundle.tgz && ARENA_DOMAIN='$ARENA_DOMAIN' CERT_EMAIL='$CERT_EMAIL' ALLOWED_ORIGINS='$ALLOWED_ORIGINS' bash deploy/install-relay.sh"
rm -f "$bundle"
echo "Health over the internet:"
curl -fsS "https://${ARENA_DOMAIN}/health" || curl -fsS "http://${ARENA_DOMAIN}/health" || true
echo
echo "Next: cd game && ARENA_URL=wss://${ARENA_DOMAIN}/ws npm run build   (then upload game/dist/ to ${ALLOWED_ORIGINS%%,*})"
