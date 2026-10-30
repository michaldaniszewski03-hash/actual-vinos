/* vinOS installer sidebar.
 *
 * Steps are numbered and set in mono; the current one gets the oxblood rule.
 * Finished steps stay readable, upcoming ones are dimmed.
 */
import io.calamares.ui 1.0
import io.calamares.core 1.0

import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: sideBar
    color: "#161210"
    anchors.fill: parent

    readonly property color paper: "#EFE8DC"
    readonly property color muted: "#8F8478"
    readonly property color dim: "#5E544B"
    readonly property color line: "#3A312B"
    readonly property color accent: "#B8505E"

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 28
        anchors.rightMargin: 20
        anchors.topMargin: 36
        anchors.bottomMargin: 24
        spacing: 0

        Image {
            source: "sidebar-logo.png"
            fillMode: Image.PreserveAspectFit
            Layout.preferredHeight: 44
            Layout.preferredWidth: sourceSize.width * 44 / sourceSize.height
            smooth: true
            mipmap: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.topMargin: 28
            Layout.bottomMargin: 20
            height: 1
            color: sideBar.line
        }

        Repeater {
            model: ViewManager

            Item {
                readonly property bool current: index === ViewManager.currentStepIndex
                readonly property bool done: index < ViewManager.currentStepIndex

                Layout.fillWidth: true
                height: 38

                Rectangle {
                    visible: current
                    x: -28
                    width: 3
                    height: parent.height
                    color: sideBar.accent
                }

                Text {
                    id: number
                    anchors.verticalCenter: parent.verticalCenter
                    text: (index + 1 < 10 ? "0" : "") + (index + 1)
                    font.family: "JetBrains Mono"
                    font.pixelSize: 11
                    color: current ? sideBar.accent : sideBar.dim
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: number.right
                    anchors.leftMargin: 14
                    anchors.right: parent.right
                    text: display
                    elide: Text.ElideRight
                    font.family: "Inter"
                    font.pixelSize: 14
                    font.weight: current ? Font.DemiBold : Font.Normal
                    color: current ? sideBar.paper : (done ? sideBar.muted : sideBar.dim)
                }
            }
        }

        Item { Layout.fillHeight: true }

        Text {
            text: "arch based · rolling"
            font.family: "JetBrains Mono"
            font.pixelSize: 11
            color: sideBar.dim
        }

        Text {
            visible: debug.enabled
            Layout.topMargin: 8
            text: "debug"
            font.family: "JetBrains Mono"
            font.pixelSize: 11
            font.underline: true
            color: sideBar.muted
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: debug.toggle()
            }
        }
    }
}
