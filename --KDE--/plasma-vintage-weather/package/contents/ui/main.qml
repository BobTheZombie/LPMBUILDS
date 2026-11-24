import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import "WeatherApi.js" as Weather

PlasmoidItem {
    id: root
    implicitWidth: 730
    implicitHeight: 405
    toolTipMainText: i18n("Aurora Vintage Weather")
    toolTipSubText: locationName + " • " + status

    property var clockTime: new Date()
    property var weather: null
    property string locationName: plasmoid.configuration.location || "Set your city"
    property string status: i18n("Waiting for forecast")
    property bool loading: false
    property int requestSerial: 0
    property string cachedLookup: ""
    property var cachedCoordinates: null
    readonly property bool narrow: width < 560
    readonly property string unitMark: plasmoid.configuration.temperatureUnit === "celsius" ? "C" : "F"
    readonly property var current: weather && weather.current ? weather.current : null
    readonly property var daily: weather && weather.daily ? weather.daily : null
    readonly property string description: current ? Weather.description(current.weather_code, !!current.is_day) : "Awaiting clear skies"
    readonly property int code: current ? current.weather_code : 2
    readonly property bool daytime: current ? !!current.is_day : true

    function refreshNow() {
        var key=(plasmoid.configuration.location||"").trim()+"|"+(plasmoid.configuration.countryCode||"US").trim();
        var serial=++root.requestSerial;
        if(!key.split("|")[0]) { loading=false; status=i18n("Configure a city"); return; }
        loading=true;
        status=i18n("Updating conditions…");
        if(cachedCoordinates && cachedLookup===key) {
            requestForecast(cachedCoordinates,serial);
            return;
        }
        Weather.requestJson(Weather.geocodeUrl(plasmoid.configuration.location,plasmoid.configuration.countryCode), function(data,error){
            if(serial!==root.requestSerial) return;
            var match=data ? Weather.bestLocation(data.results,plasmoid.configuration.location) : null;
            if(!match) {
                loading=false;status=error || i18n("City not found");
                return;
            }
            cachedCoordinates={lat:match.latitude,lon:match.longitude};
            cachedLookup=key;
            locationName=match.name+(match.admin1?", "+match.admin1:"");
            requestForecast(cachedCoordinates,serial);
        });
    }
    function requestForecast(coords,serial) {
        var url=Weather.forecastUrl(coords.lat,coords.lon,plasmoid.configuration.temperatureUnit);
        Weather.requestJson(url,function(data,error) {
            if(serial!==root.requestSerial) return;
            loading=false;
            if(!data || !data.current || !data.daily || !data.daily.time) {
                status=error || i18n("Weather service unavailable");
                return;
            }
            weather=data;
            var stamp=data.current.time || "";
            status=i18n("Updated %1",stamp.indexOf("T")>=0?stamp.split("T")[1]:"now");
        });
    }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.clockTime=new Date() }
    Timer {
        id: updateTimer
        interval: Math.max(10,Math.min(60,plasmoid.configuration.refreshMinutes || 20))*60000
        running: true; repeat: true
        onTriggered: root.refreshNow()
    }
    Connections {
        target: plasmoid.configuration
        function onLocationChanged() { root.cachedLookup="";root.refreshNow(); }
        function onCountryCodeChanged() { root.cachedLookup="";root.refreshNow(); }
        function onTemperatureUnitChanged() { root.refreshNow(); }
    }
    Component.onCompleted: root.refreshNow()

    Rectangle {
        anchors.fill: parent
        radius: 22
        border.color: "#99775b"
        border.width: 1.3
        gradient: Gradient {
            GradientStop { position: 0; color: "#302d3b" }
            GradientStop { position: .46; color: "#161f34" }
            GradientStop { position: 1; color: "#0c1323" }
        }
    }
    Rectangle {
        anchors.fill: parent
        anchors.margins: 7
        radius: 17
        color: "transparent"
        border.color: "#617e837b"
        border.width: 1
    }
    GridLayout {
        anchors.fill: parent
        anchors.margins: 17
        columns: root.narrow ? 1 : 2
        columnSpacing: 18
        rowSpacing: 7
        Item {
            Layout.alignment: Qt.AlignHCenter|Qt.AlignVCenter
            Layout.preferredWidth: root.narrow ? root.width-40 : Math.min(root.width*.43,root.height-38)
            Layout.preferredHeight: root.narrow ? Math.min(245,root.height*.43) : root.height-38
            AntiqueClock {
                anchors.centerIn: parent
                width: Math.min(parent.width,parent.height)
                height: width
                dateTime: root.clockTime
                showSeconds: plasmoid.configuration.showSeconds
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 7
            RowLayout {
                Layout.fillWidth: true
                spacing: 6
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 1
                    Text {
                        text: "A U R O R A   /   V I N T A G E"
                        color: "#edc98d"
                        font.pixelSize: 11
                        font.bold: true
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Text {
                        text: root.locationName
                        color: "#fff3de"
                        font.pixelSize: 18
                        font.family: "Noto Serif"
                        font.bold: true
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
                Rectangle {
                    width: 32; height: 32
                    radius: 16
                    color: refreshArea.containsMouse ? "#4c6584" : "#334354"
                    border.color: "#907b5b"
                    Text { anchors.centerIn: parent; text: "↻"; color: "#fff0d5"; font.pixelSize: 25 }
                    MouseArea {
                        id: refreshArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: root.refreshNow()
                        enabled: !root.loading
                    }
                }
            }
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: root.narrow ? 88 : Math.max(90,root.height*.29)
                clip: true
                Rectangle { anchors.fill: parent; radius: 13; color: "#3c5869" }
                WeatherScene {
                    anchors.fill: parent
                    weatherCode: root.code
                    isDay: root.daytime
                    animated: plasmoid.configuration.animations
                }
                Rectangle {
                    anchors.fill: parent
                    radius: 13; color: "transparent"
                    border.color: "#d6ba856e";border.width: 1
                }
                Column {
                    anchors.left: parent.left
                    anchors.leftMargin: 14
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 0
                    Text {
                        text: root.current ? Weather.formatDegree(root.current.temperature_2m) : "—°"
                        font.family: "Noto Serif"
                        font.pixelSize: Math.min(51,Math.max(34,root.width*.065))
                        font.bold: true
                        color: "#fffdf0"
                        style: Text.Outline;styleColor: "#26384b"
                    }
                    Text {
                        text: root.description
                        font.pixelSize: 12
                        font.bold: true
                        color: "#ffffff"
                        style: Text.Outline;styleColor: "#24384b"
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: 4
                Text {
                    text: root.current ? "FEELS "+Weather.formatDegree(root.current.apparent_temperature) : "FEELS —"
                    color: "#f9e0b7";font.pixelSize: 11
                    Layout.fillWidth: true
                }
                Text {
                    text: root.current ? "HUMIDITY "+root.current.relative_humidity_2m+"%" : "HUMIDITY —"
                    color: "#d8e2ef";font.pixelSize: 11
                }
            }
            Text {
                text: root.current ? "WIND  "+Math.round(root.current.wind_speed_10m)+(root.unitMark==="F"?" mph":" km/h") : "WIND —"
                color: "#c4d1e0"; font.pixelSize: 11
            }
            Rectangle { Layout.fillWidth:true;Layout.preferredHeight:1;color:"#876a4c" }
            Text {
                text: "THE DAYS AHEAD"
                color: "#d4b482";font.pixelSize: 11; font.bold: true
                font.letterSpacing: 1.7
            }
            RowLayout {
                Layout.fillWidth:true
                spacing: 2
                Repeater {
                    model: root.daily ? Math.min(4,root.daily.time.length) : 4
                    delegate: ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: root.daily ? Qt.formatDate(new Date(root.daily.time[index]+"T12:00:00"),"ddd") : "—"
                            color: "#e6d2b9";font.pixelSize: 11
                        }
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: root.daily ? Weather.glyph(root.daily.weather_code[index],true) : "☀"
                            color: "#f6d49a";font.pixelSize: 25
                        }
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: root.daily ? Math.round(root.daily.temperature_2m_max[index])+"° / "+Math.round(root.daily.temperature_2m_min[index])+"°" : "— / —"
                            color: "#ffffff";font.pixelSize: 11
                        }
                    }
                }
            }
            Item {Layout.fillHeight:true}
            RowLayout {
                Layout.fillWidth:true
                Text {
                    Layout.fillWidth:true
                    text: root.status
                    color: root.loading ? "#ecd29a" : "#9ab4c3"
                    font.pixelSize: 10;elide:Text.ElideRight
                }
                Text {
                    text: Qt.formatDateTime(root.clockTime,plasmoid.configuration.use24Hour?"ddd d MMM • HH:mm":"ddd d MMM • h:mm AP")
                    color: "#bf9f70";font.pixelSize: 10
                }
            }
            Text {
                Layout.alignment: Qt.AlignRight
                text: "Weather by Open-Meteo • GeoNames"
                color: "#9fb2be";font.pixelSize: 9
                MouseArea {
                    anchors.fill:parent
                    cursorShape:Qt.PointingHandCursor
                    onClicked: Qt.openUrlExternally("https://open-meteo.com/")
                }
            }
        }
    }
}
