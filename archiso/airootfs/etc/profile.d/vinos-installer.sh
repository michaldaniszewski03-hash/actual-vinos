# vinOS live session: start the graphical installer on the first console.
# Other consoles (Ctrl+Alt+F2..F6) give a plain root shell.
# (Lives in profile.d rather than ~/.bash_profile so the source tree has no dotfiles.)
if [[ $EUID -eq 0 && $(tty) == /dev/tty1 && -z $WAYLAND_DISPLAY && -x /usr/local/bin/vinos-installer ]]; then
    vinos-installer
    printf '\nThe installer closed. Run \033[1mvinos-installer\033[0m to open it again.\n\n'
fi
