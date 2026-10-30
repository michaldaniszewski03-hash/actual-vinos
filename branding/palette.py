"""vinOS palette. Single source of truth for every rendered asset.

Edit here, then run `python3 tools/render_branding.py` and commit the output.
The QSS and GRUB theme.txt reference the same hex values by hand; grep for
the old value when changing one.
"""

INK = "#161210"        # boot screen / sidebar background, warm near-black
INK_2 = "#211B18"      # raised surface on dark (selected row)
LINE_DARK = "#3A312B"  # hairlines on dark
PAPER = "#EFE8DC"      # primary text on dark, content background in installer
PAPER_2 = "#E4DACA"    # recessed surface on light
LINE_LIGHT = "#CDBFAB" # hairlines on light
MUTED = "#8F8478"      # secondary text on both
SEPIA = "#5E544B"      # body text on light
ACCENT = "#8C2F39"     # oxblood: the one accent colour
ACCENT_HI = "#B8505E"  # accent used as text/marks on dark backgrounds
