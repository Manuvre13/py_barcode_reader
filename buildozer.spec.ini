[app]
title = Barcode Reader
package.name = barcodereader
package.domain = com.yourname.barcodereader

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0
requirements = python3,kivy,opencv,pyzbar,pillow,numpy

[buildozer]
log_level = 2

[app]
# Android specific
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, VIBRATE
android.api = 30
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# Optimization for GitHub Actions
android.gradle_dependencies = 

# Skip some checks for faster builds
android.skip_update = False
android.debug = 1