[app]
# (str) Title of your application
title = Gordinchis
# (str) Package name
package.name = gordinchis
# (str) Package domain (needed for Android/iOS packaging)
package.domain = org.rauh1702
# (str) Source code where main.py lives
source.dir = .
# (str) Main Python file
source.include_exts = py,png,jpg,jpeg,mp3,wav,mp4,zip
# (str) Version
version = 1.0
# (str) Application requirements
requirements = python3,kivy,numpy
# (str) Supported orientation
orientation = landscape

[buildozer]
log_level = 2
warn_on_root = 0

[android]
# Android SDK/NDK configuration
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master
android.presplash_color = #FFFFFF
android.enable_androidx = True
# Use the SDK prepared by GitHub Actions instead of Buildozer downloading its own old SDK.
android.sdk_path = %(source.dir)s/.buildozer/android/platform/android-sdk
android.skip_update = True
android.accept_sdk_license = True
