# vinOS

An Arch-based Linux distribution with its own graphical installer, boot theme and fastfetch logo.

![GRUB](docs/screenshots/grub.png)

| Installer | Desktop choice |
|---|---|
| ![Welcome](docs/screenshots/installer-welcome.png) | ![Desktop](docs/screenshots/installer-desktop.png) |

*(The requirement warnings in the welcome screenshot come from the machine they were taken on, which had no disk and no network.)*

## What's here

| Path | What it is |
|---|---|
| `archiso/` | The archiso profile: package list, live root filesystem, BIOS (syslinux) and UEFI (GRUB) boot menus |
| `calamares/` | Installer configuration and the `vinos` branding: stylesheet, sidebar, slideshow, images |
| `grub/themes/vinos/` | GRUB theme, used on the live USB (UEFI) and on installed systems |
| `fastfetch/` | fastfetch config and the vinOS ASCII logo |
| `desktop/` | Wallpapers and default settings for KDE Plasma and GNOME, copied into the system as-is |
| `branding/` | Palette, logo files, fonts |
| `pkg/calamares/` | PKGBUILD for Calamares (not in the official Arch repos) |
| `tools/` | Asset renderers and the Calamares build helper |
| `build.sh` | Builds the ISO |
| `.github/workflows/build.yml` | Builds the ISO on GitHub |

## Getting an ISO

### On GitHub (no Arch machine needed)

1. Push this repository to GitHub.
2. Open the **Actions** tab. The *Build ISO* workflow runs on every push to `main` (you can also start it by hand with *Run workflow*).
3. When it finishes, download `vinos-iso` from the run's **Artifacts** section. It's a zip containing the `.iso` and its `.sha256`.

To publish a release, push a tag. The workflow attaches the ISO to a GitHub Release:

```bash
git tag v2026.11
```

```bash
git push origin v2026.11
```

A build takes roughly 30–60 minutes, most of it compiling Calamares.

**Uploading through the GitHub website works.** Nothing in the tree depends on hidden files (other than `.github/`), symlinks or executable bits surviving; `build.sh` creates those during the build. If you upload by drag-and-drop, check that the `.github` folder made it, since Finder and file pickers hide it.

### Locally, on Arch

```bash
sudo pacman -S --needed archiso grub git base-devel
```

```bash
sudo bash build.sh
```

The ISO is written to `out/`. Intermediate files go to `work/` (safe to delete).

### Trying it in a VM

```bash
run_archiso -u -i out/vinos-*.iso
```

(`run_archiso` comes with the `archiso` package; `-u` boots UEFI so you see the GRUB theme. Drop `-u` for the BIOS menu.)

## How the install works

The live USB boots straight into the installer: root is logged in automatically on tty1, which starts a full-screen `cage` session (a single-window Wayland kiosk). Ctrl+Alt+F2 gives a plain root shell.

1. **Network.** If there's no connection after a few seconds but there is Wi-Fi hardware, a short "Connect to the internet" screen comes first, with `nmtui` for picking a network. Ethernet connects on its own and skips this. It can be skipped; the base system installs offline.
2. **Installer.** Calamares asks for language, location, keyboard, desktop, disk and account, then installs.
3. **Base system.** Calamares copies the live root filesystem to disk, then `vinos-postinstall` removes the live-session pieces (autologin, the archiso initramfs hooks, the installer) and sets up the pacman keyring. Then the initramfs, users, services, and GRUB with the vinOS theme.
4. **Desktop.** Installed last, by `vinos-install-desktop`, with no questions asked (below).

The installed system includes `base-devel`, PipeWire audio, Bluetooth, NetworkManager, firmware for most laptops' sound, fastfetch and the usual command-line tools.

### Desktop choices

The **Desktop** page offers:

| Choice | What's installed |
|---|---|
| **Hyprland** (default), **niri**, **Sway**, **MangoWC** | [serpantinum](https://github.com/ilyamiro/serpantinum) by ilyamiro on that compositor, with SDDM |
| **KDE Plasma** | Plasma, SDDM, Konsole, Dolphin, Kate, Ark, Spectacle, Gwenview, Okular, Firefox, Flatpak; vinOS wallpaper on desktop, lock screen and login |
| **GNOME** | GNOME with GDM, GNOME Tweaks, Firefox, Flatpak; vinOS wallpaper (dark and light) |
| **Base system only** | Console login; works offline |

Everything after picking is unattended. `vinos-install-desktop` runs inside the new system after the bootloader is installed, so a failure can never leave the machine unbootable. It refreshes the mirror list with reflector, installs the packages, enables the login manager and boots to it. If it fails (no network, a package error), the install still finishes. `/var/log/vinos-install-desktop.log` has the details, and the console login screen shows the exact command to retry.

### vinos-desktop: serpantinum, without the menu

The serpantinum options use **`vinos-desktop`** (`archiso/airootfs/usr/local/bin/vinos-desktop`), vinOS's edition of serpantinum's `install/install.sh`. It's a modified copy under the same licence (AGPL-3.0-or-later), with ilyamiro's copyright kept. Changes from upstream, also listed in the file header:

- **No interactive menu.** The compositor comes from `--compositor`, then from what's already installed, then Hyprland. Wallpapers: full pack. Login manager: SDDM.
- **Unattended.** During installation it asks nothing. Run later by hand, it asks for the sudo password once and keeps it fresh through long AUR builds. yay and paru review menus are switched off, unless the user already has their own config.
- **No telemetry.** The calls are removed, not just switched off.
- **vinOS is a supported distribution**, so the upstream "unsupported OS" check passes.
- **Pinned upstream version.** It checks out a reviewed serpantinum commit (`VINOS_SERPANTINUM_REF`) instead of `master`; `--ref master` overrides it.
- **No completion screen or restart prompt.** Output is plain log lines.

It stays installed, so users update or switch compositor themselves:

```bash
vinos-desktop
```

```bash
vinos-desktop --compositor niri
```

**Updating the pinned commit:** diff upstream's `install/install.sh` against `vinos-desktop`, carry over any new steps, then bump `VINOS_SERPANTINUM_REF`.

## Changing the look

All colours come from `branding/palette.py`. After editing it:

```bash
python3 tools/render_branding.py
```

```bash
python3 tools/render_ascii.py > fastfetch/vinos.txt
```

These regenerate every image (GRUB, syslinux splash, installer images, Desktop-page cards, wallpapers, logos) and the fastfetch logo. `stylesheet.qss`, `calamares-sidebar.qml`, `show.qml`, `theme.txt` and the syslinux config use the same hex values written out by hand; grep for the old value.

GRUB fonts are bitmap `.pf2` files. To change the font or size:

```bash
grub-mkfont -s 22 -o grub/themes/vinos/jetbrains-mono-22.pf2 branding/fonts/JetBrainsMono-Regular.ttf
```

## Testing status

What has been run, and what hasn't:

- **GRUB theme:** rendered by real GRUB 2.12 booted in QEMU; the screenshot above is from that.
- **Installer pages:** rendered by a real Calamares 3.3 binary with this config and branding. The screenshots are from that.
- **Slideshow:** rendered through Calamares' slideshow QML module.
- **Wi-Fi screen:** rendered in a real `cage` and `foot` session.
- **`build.sh`:** dry run checks that every file `mkarchiso` sets permissions on exists in the assembled profile. A missing one is the most common way an archiso build breaks.
- **Shell scripts:** pass `shellcheck`.
- **`vinos-desktop`:** run as a normal user against a vinOS `os-release`, up to the point where it installs packages. Covered: the distro check, compositor selection and defaults, rejection of unknown compositors and non-Arch systems, telemetry off, pinned commit.
- **Not run yet:** `mkarchiso`, the Calamares PKGBUILD build, a full end-to-end install, serpantinum's package and config steps, and the KDE Plasma and GNOME installs. All of these need an Arch host. The first GitHub Actions run is the real test of the ISO build; after that, do a test install in a VM before handing the ISO to anyone.

## Licences

- Instrument Serif and JetBrains Mono: SIL Open Font License (see `branding/fonts/`).
- Calamares: GPL-3.0-or-later.
- serpantinum: see its repository.
- Boot configs in `archiso/`: derived from archiso's `releng` profile (GPL-3.0-or-later).
