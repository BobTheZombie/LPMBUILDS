# LPM Linux: Plasma 6.8.1 shutdown / reboot / logout repair

Plasma 6.8.1-7 patches the logout greeter to query the shutdown state
rather than treating mere org.kde.Shutdown name ownership as logout in progress.
The recipe also verifies both D-Bus activation files and their binaries.
No polkit rules or permission bypasses are installed.

## Check from a running desktop session (do not use sudo)

```sh
loginctl show-session "${XDG_SESSION_ID:?No registered logind session}" -p Active -p Type -p Class -p State
systemctl is-active systemd-logind
systemctl --user is-active plasma-ksmserver.service
ls -l /usr/share/dbus-1/services/org.kde.LogoutPrompt.service
ls -l /usr/share/dbus-1/services/org.kde.Shutdown.service
grep '^Exec=' /usr/share/dbus-1/services/org.kde.{LogoutPrompt,Shutdown}.service
# Safe read-only state probe; does not shut down:
busctl --user call org.kde.Shutdown /Shutdown org.kde.Shutdown isLogoutInProgress
# Safe capability probes; no shutdown requests:
busctl --system call org.freedesktop.login1 /org/freedesktop/login1 org.freedesktop.login1.Manager CanPowerOff
busctl --system call org.freedesktop.login1 /org/freedesktop/login1 org.freedesktop.login1.Manager CanReboot
```

Expected: active local Wayland logind session, available D-Bus service files,
b false idle shutdown state, and yes or challenge for power capabilities.

To test only the confirmation dialog, without ending your session:

```sh
busctl --user call org.kde.LogoutPrompt /LogoutPrompt org.kde.LogoutPrompt promptAll
```

Click Cancel. A failing confirmation/actual power request may indicate a
different issue from the unresponsive launcher's D-Bus activation.
Capture relevant diagnostics without actually requesting poweroff:

```sh
journalctl --user -b --no-pager -n 150 -g 'ksmserver|logout-greeter|plasma-shutdown|org.kde.Shutdown'
journalctl -b -u systemd-logind --no-pager -n 80
```

If login1 reports InteractiveAuthorizationRequired, verify the session is
registered through SDDM and pam_systemd. Avoid broad polkit permission
overrides. Restart the desktop session after installing the rebuilt package
so the new binaries and D-Bus contract are picked up.
