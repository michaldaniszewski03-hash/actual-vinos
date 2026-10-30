// vinOS: set the default wallpaper once per user, the first time Plasma starts.
// Plasma runs each script in this directory once and remembers it.
var all = desktops();
for (var i = 0; i < all.length; i++) {
    var d = all[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "file:///usr/share/backgrounds/vinos/vinos-dark.jpg");
    d.writeConfig("FillMode", "2");
}
