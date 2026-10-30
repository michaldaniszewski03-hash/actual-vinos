#!/usr/bin/env bash
# Build pkg/calamares into a local pacman repository at $1.
# Needs root (installs build dependencies); makepkg itself runs as an
# unprivileged user because it refuses to run as root.
set -euo pipefail

repo="$(realpath -m "${1:?usage: build-calamares.sh <repo-dir>}")"
root="$(cd "$(dirname "$0")/.." && pwd)"
builder=vinos-build

mkdir -p "$repo"
if compgen -G "$repo/calamares-*.pkg.tar.zst" >/dev/null; then
    echo ":: calamares already built in $repo"
    exit 0
fi

# shellcheck source=/dev/null disable=SC2154
read -ra deps < <(source "$root/pkg/calamares/PKGBUILD"; echo "${depends[@]}" "${makedepends[@]}")
pacman -S --needed --noconfirm base-devel "${deps[@]}"

id "$builder" &>/dev/null || useradd --system --create-home "$builder"
build="$(runuser -u "$builder" -- mktemp -d)"
cp "$root/pkg/calamares/PKGBUILD" "$build/"
chown -R "$builder:" "$build"
runuser -u "$builder" -- bash -c "cd '$build' && makepkg --noconfirm --cleanbuild"

cp "$build"/calamares-*.pkg.tar.zst "$repo/"
repo-add "$repo/vinos-local.db.tar.gz" "$repo"/calamares-*.pkg.tar.zst
rm -rf "$build"
