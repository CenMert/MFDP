#!/usr/bin/env bash
# MFDP KDE panel widget'ını kurar / günceller.
# Sonra: panele sağ tık → "Widget ekle" → "MFDP Timer"
set -e
cd "$(dirname "$0")"
PKG=plasmoid/org.mfdp.timer
if kpackagetool6 -t Plasma/Applet -l | grep -q org.mfdp.timer; then
    kpackagetool6 -t Plasma/Applet -u "$PKG"
else
    kpackagetool6 -t Plasma/Applet -i "$PKG"
fi
echo "Kuruldu. Widget görünmezse: plasmashell --replace &"
