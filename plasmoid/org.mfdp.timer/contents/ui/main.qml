import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    // MFDP uygulamasının yazdığı durum (core/panel_bridge.py)
    property bool appOpen: false
    property bool running: false
    property string mode: "countdown"
    property int baseSeconds: 0
    property string dotColor: ""
    property double receivedAt: 0
    property int tick: 0   // süreyi yeniden hesaplatmak için

    readonly property string readCmd: "cat \"${XDG_RUNTIME_DIR}/mfdp/state.json\" 2>/dev/null"
    readonly property string toggleCmd: "busctl --user call org.mfdp.Timer /Timer org.mfdp.Timer Toggle"

    Plasmoid.status: PlasmaCore.Types.ActiveStatus
    preferredRepresentation: fullRepresentation

    function currentSeconds() {
        tick; // bağımlılık
        if (!running)
            return baseSeconds;
        var dt = Math.floor((Date.now() - receivedAt) / 1000);
        return mode === "countup" ? baseSeconds + dt : Math.max(0, baseSeconds - dt);
    }

    function format(s) {
        var m = Math.floor(s / 60), r = s % 60;
        return (m < 10 ? "0" : "") + m + ":" + (r < 10 ? "0" : "") + r;
    }

    function applyState(text) {
        var st = null;
        try { st = JSON.parse(text); } catch (e) { st = null; }
        if (!st || (Date.now() / 1000 - st.ts) > 3) {
            appOpen = false;
            return;
        }
        appOpen = true;
        running = st.running;
        mode = st.mode;
        baseSeconds = st.seconds;
        dotColor = st.color || "";
        receivedAt = Date.now();
    }

    P5Support.DataSource {
        id: exec
        engine: "executable"
        connectedSources: []
        onNewData: (source, data) => {
            if (source === root.readCmd)
                root.applyState(data["stdout"] || "");
            disconnectSource(source);
        }
    }

    Timer {
        interval: 2000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: exec.connectSource(root.readCmd)
    }

    Timer {
        interval: 500
        running: root.appOpen
        repeat: true
        onTriggered: root.tick++
    }

    fullRepresentation: MouseArea {
        id: area
        readonly property real dotSize: Kirigami.Units.gridUnit * 0.7
        Layout.minimumWidth: root.appOpen ? row.implicitWidth + Kirigami.Units.smallSpacing * 2 : Kirigami.Units.iconSizes.medium
        Layout.preferredWidth: Layout.minimumWidth
        Layout.maximumWidth: Layout.minimumWidth
        hoverEnabled: true
        cursorShape: root.appOpen ? Qt.PointingHandCursor : Qt.ArrowCursor

        // MFDP kapalıyken soluk simge (widget bulunabilir kalsın)
        Kirigami.Icon {
            anchors.centerIn: parent
            width: Math.min(parent.height, Kirigami.Units.iconSizes.medium)
            height: width
            source: "chronometer"
            opacity: 0.4
            visible: !root.appOpen
        }

        onClicked: {
            if (!root.appOpen)
                return;
            exec.connectSource(root.toggleCmd);
            // hızlı geri bildirim: yerelde de durumu çevir, bir sonraki okuma düzeltir
            root.baseSeconds = root.currentSeconds();
            root.receivedAt = Date.now();
            root.running = !root.running;
        }

        RowLayout {
            id: row
            visible: root.appOpen
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing

            Rectangle {
                Layout.preferredWidth: area.dotSize
                Layout.preferredHeight: area.dotSize
                radius: width / 2
                color: root.dotColor !== "" ? root.dotColor : Kirigami.Theme.disabledTextColor
                opacity: root.running ? 1.0 : 0.5
            }

            Text {
                text: root.format(root.currentSeconds())
                color: Kirigami.Theme.textColor
                opacity: root.running ? 1.0 : 0.5
                font.pixelSize: Math.min(area.height * 0.5, Kirigami.Units.gridUnit * 1.2)
                font.bold: true
                font.family: Kirigami.Theme.fixedWidthFont.family
            }
        }
    }
}
