import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: page
    property alias cfg_location: location.text
    property alias cfg_countryCode: country.text
    property string cfg_temperatureUnit: "fahrenheit"
    property alias cfg_refreshMinutes: refresh.value
    property alias cfg_animations: animations.checked
    property alias cfg_showSeconds: seconds.checked
    property alias cfg_use24Hour: hour24.checked

    QQC2.TextField {
        id: location
        Kirigami.FormData.label: i18n("City, region:")
        placeholderText: i18n("e.g. Watervliet, Michigan")
    }
    QQC2.TextField {
        id: country
        Kirigami.FormData.label: i18n("Country code:")
        placeholderText: "US"
        maximumLength: 2
    }
    QQC2.ComboBox {
        id: units
        Kirigami.FormData.label: i18n("Temperature:")
        model: [i18n("Fahrenheit (°F)"), i18n("Celsius (°C)")]
        currentIndex: page.cfg_temperatureUnit === "celsius" ? 1 : 0
        onActivated: page.cfg_temperatureUnit = currentIndex === 1 ? "celsius" : "fahrenheit"
    }
    QQC2.SpinBox {
        id: refresh
        Kirigami.FormData.label: i18n("Refresh (minutes):")
        from: 10; to: 60
        editable: true
    }
    QQC2.CheckBox {
        id: animations
        text: i18n("Animate sun, clouds, rain and snow")
    }
    QQC2.CheckBox {
        id: seconds
        text: i18n("Show sweeping second hand")
    }
    QQC2.CheckBox {
        id: hour24
        text: i18n("24-hour digital date/time footer")
    }
    QQC2.Label {
        text: i18n("Weather: Open-Meteo. Location search: GeoNames via Open-Meteo. A network connection is required.")
        wrapMode: Text.WordWrap
        Layout.fillWidth: true
        opacity: 0.75
    }
}
