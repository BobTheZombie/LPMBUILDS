LPM Linux - Qt6Bluetooth 6.12.0
================================

The upstream Qt6Bluetooth module comes from qtconnectivity, not a separate
qtbluetooth source archive. This recipe builds Qt6Bluetooth and Qt6Nfc
against an existing QtBase 6.12.0, with a real Linux BlueZ backend.

Install/build:
    qt6-base 6.12.0
    BlueZ libraries + development headers (bluez.pc)
    qt6-connectivity 6.12.0

The LPM package is named "qt6-connectivity" and PROVIDES the aliases
"Qt6Bluetooth", "qt6-bluetooth", "Qt6Nfc", and "qt6-nfc".

If your own LPM index names the BlueZ library package "bluez-libs", adjust
the bluez entry under REQUIRES and BUILD_REQUIRES to match your provider.
CMake feature FEATURE_bluez=ON will refuse a dummy backend if BlueZ is absent.

Expected installed files:
    /usr/lib/libQt6Bluetooth.so*
    /usr/lib/libQt6Nfc.so*
    /usr/lib/cmake/Qt6Bluetooth/Qt6BluetoothConfig.cmake
    /usr/lib/cmake/Qt6Nfc/Qt6NfcConfig.cmake
    /usr/include/qt6/QtBluetooth/

Qt6 Bluetooth CMake usage:
    find_package(Qt6 REQUIRED COMPONENTS Bluetooth)
    target_link_libraries(myapp PRIVATE Qt6::Bluetooth)

Qt6 Bluetooth depends on the BlueZ 5.x userspace stack on Linux. For runtime
Bluetooth device operations, bluetoothd and the system D-Bus are required.
NFC backends may require pcsclite or neard for actual NFC hardware.

SHA256SUMS is currently SKIP: verify archive checksum before repository
publication. The package recipe passed bash -n; full build requires an
LPM Linux chroot with QtBase 6.12.0.
