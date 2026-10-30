#!/usr/bin/env bash
# shellcheck disable=SC2034

iso_name="vinos"
iso_label="VINOS_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="vinOS"
iso_application="vinOS live installer"
iso_version="$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y.%m.%d)"
install_dir="vinos"
buildmodes=('iso')
bootmodes=('bios.syslinux'
           'uefi.grub')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15' '-b' '1M')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/.bash_profile"]="0:0:644"
  ["/usr/local/bin/vinos-installer"]="0:0:755"
  ["/usr/local/bin/vinos-postinstall"]="0:0:755"
  ["/usr/local/bin/vinos-serpantinum"]="0:0:755"
  ["/usr/local/bin/vinos-desktop"]="0:0:755"
)
