[app]
# (str) Title of your application
 title = Gordinchis
# (str) Package name
package.name = gordinchis
# (str) Package domain (needed for android/ios packaging)
package.domain = org.rauh1702
# (str) Source code where main.py lives
source.dir = .
# (str) Main Python file
source.include_exts = py,png,jpg,jpeg,mp3,wav,mp4,zip
# (str) Version
version = 1.0
# (str) Application requirements
requirements = python3,kivy,numpy
# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape
# (str) Full name including package domain
# package.name + package.domain determines the Android application id

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# (str) Android API to use
android.api = 35
# (str) Minimum API your app supports
android.minapi = 23
# (str) Android NDK version
android.ndk = 27c
# (str) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a
# (str) Python-for-Android branch to use
p4a.branch = master
# (str) Android app theme
android.presplash_color = #FFFFFF
# (bool) Enable AndroidX support
android.enable_androidx = True
# Automatically accept Android SDK licenses during automated builds
android.accept_sdk_license = True
