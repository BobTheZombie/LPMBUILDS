/* Plasma Aurora v0.3: opt-in desktop layout. Uses upstream widgets. */
var dock = new Panel();
dock.location = "bottom";
dock.alignment = "center";
dock.lengthMode = "fit";
dock.height = Math.round(gridUnit * 3);
dock.hiding = "dodgewindows";
dock.addWidget("org.kde.plasma.kickoff");
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "applications:org.kde.dolphin.desktop,applications:org.kde.konsole.desktop");
dock.addWidget("org.kde.plasma.systemtray");
dock.addWidget("org.kde.plasma.digitalclock");
dock.addWidget("org.kde.plasma.showdesktop");
/* Plasma floating mode must be enabled in the panel editor if unsupported by the scripting API. */
