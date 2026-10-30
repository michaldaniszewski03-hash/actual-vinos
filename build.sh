#!/usr/bin/env bash
# Build the vinOS ISO. Run as root on Arch Linux (or in an archlinux container
# with --privileged). Output lands in ./out.
#
#   sudo bash build.sh
#
# Needs: archiso grub git base-devel  (pacman -S --needed archiso grub git base-devel)

set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
work="${WORK_DIR:-$root/work}"
out="${OUT_DIR:-$root/out}"
profile="$work/profile"

die() { echo "error: $*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "run as root (mkarchiso needs it): sudo bash build.sh"
command -v mkarchiso >/dev/null || die "archiso is not installed: pacman -S archiso"
command -v grub-mkstandalone >/dev/null || die "grub is not installed: pacman -S grub"

echo ":: building calamares"
bash "$root/tools/build-calamares.sh" "$work/repo"

echo ":: assembling profile in $profile"
rm -rf "$profile"
cp -a "$root/archiso" "$profile"
air="$profile/airootfs"

# GRUB theme: on the ISO (live UEFI menu) and in the root fs (installed system)
mkdir -p "$profile/grub/themes" "$air/usr/share/grub/themes"
cp -a "$root/grub/themes/vinos" "$profile/grub/themes/"
cp -a "$root/grub/themes/vinos" "$air/usr/share/grub/themes/"

# Installer config and branding
mkdir -p "$air/etc/calamares"
cp -a "$root/calamares/." "$air/etc/calamares/"

# Fonts not packaged in Arch
install -Dm644 -t "$air/usr/share/fonts/vinos" "$root"/branding/fonts/InstrumentSerif-*.ttf
install -Dm644 "$root/branding/fonts/OFL-InstrumentSerif.txt" "$air/usr/share/licenses/vinos-fonts/OFL-InstrumentSerif.txt"

# fastfetch
install -Dm644 "$root/fastfetch/config.jsonc" "$air/etc/xdg/fastfetch/config.jsonc"
install -Dm644 "$root/fastfetch/vinos.txt" "$air/usr/share/vinos/fastfetch/vinos.txt"

# Logo for anything that looks up the os-release LOGO= icon name
install -Dm644 "$root/branding/logo/vinos-mark-dark.svg" "$air/usr/share/icons/hicolor/scalable/apps/vinos.svg"
install -Dm644 "$root/branding/logo/vinos-mark-dark.svg" "$air/usr/share/pixmaps/vinos.svg"

# Local repo with the calamares package
cat >>"$profile/pacman.conf" <<CONF

[vinos-local]
SigLevel = Optional TrustAll
Server = file://$work/repo
CONF

echo ":: running mkarchiso"
rm -rf "$work/mkarchiso"
mkarchiso -v -w "$work/mkarchiso" -o "$out" "$profile"

cd "$out"
for iso in *.iso; do sha256sum "$iso" >"$iso.sha256"; done
echo ":: done"
ls -lh "$out"
