/* vinOS install slideshow (shown while files are being copied).
 *
 * Plain paper, a serif headline, two lines of useful text. Slides advance
 * every 10 s; the last one stays up until the install finishes.
 */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation

    readonly property color paper: "#EFE8DC"
    readonly property color ink: "#161210"
    readonly property color sepia: "#5E544B"
    readonly property color accent: "#8C2F39"

    Timer {
        interval: 10000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: {
            if (presentation.currentSlide < presentation.slides.length - 1)
                presentation.goToNextSlide()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: presentation.paper
        z: -1
    }

    component VinSlide: Slide {
        id: slide
        property string kicker
        property string headline
        property string body

        Column {
            anchors.left: parent.left
            anchors.leftMargin: Math.max(40, parent.width * 0.08)
            anchors.verticalCenter: parent.verticalCenter
            width: Math.min(parent.width * 0.8, 620)
            spacing: 18

            Text {
                text: slide.kicker
                font.family: "JetBrains Mono"
                font.pixelSize: 12
                font.letterSpacing: 1.5
                color: presentation.accent
            }

            Text {
                width: parent.width
                text: slide.headline
                wrapMode: Text.WordWrap
                font.family: "Instrument Serif"
                font.pixelSize: 46
                lineHeight: 1.05
                color: presentation.ink
            }

            Text {
                width: parent.width
                text: slide.body
                wrapMode: Text.WordWrap
                textFormat: Text.RichText
                font.family: "Inter"
                font.pixelSize: 15
                lineHeight: 1.45
                color: presentation.sepia
            }
        }
    }

    VinSlide {
        kicker: "01 / 04"
        headline: "Copying vinOS to your disk."
        body: "This takes a few minutes. Nothing needs your attention until it's done."
    }

    VinSlide {
        kicker: "02 / 04"
        headline: "Arch underneath."
        body: "vinOS uses the Arch Linux repositories directly. Update everything with "
            + "<font face='JetBrains Mono'>sudo&nbsp;pacman&nbsp;\u2011Syu</font>, and anything in the Arch Wiki applies as written."
    }

    VinSlide {
        kicker: "03 / 04"
        headline: "Your desktop comes last."
        body: "KDE Plasma, GNOME or serpantinum is downloaded and set up after the base "
            + "system is in place. That part needs the network and can take a while, so the "
            + "bar may sit near the end for some minutes."
    }

    VinSlide {
        kicker: "04 / 04"
        headline: "After the reboot."
        body: "Log in with the account you just created. Run <font face='JetBrains Mono'>nmtui</font> "
            + "to join Wi-Fi, then <font face='JetBrains Mono'>fastfetch</font> to make sure you're home."
    }

    function onActivate() {
        presentation.currentSlide = 0
    }

    function onLeave() {
    }
}
