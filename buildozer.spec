[app]
# Basic app info
title = Barcode Reader
package.name = barcodereader
package.domain = com.yourname.barcodereader

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version
version = 1.0

# Requirements - using specific versions for stability
requirements = python3,kivy==2.1.0,opencv==4.5.1.48,pyzbar,pillow,numpy,android

# Optional requirements
#garden_requirements =

[buildozer]
# Buildozer log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Build directory
build_dir = /tmp/kivy_build

# Buildozer cache directory
cache_dir = /tmp/kivy_cache

[app:android]
# Android specific settings
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,VIBRATE,INTERNET

# Android API versions
android.api = 30
android.minapi = 21
android.ndk = 25c
android.sdk = 33

# Accept SDK license automatically
android.accept_sdk_license = True

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Skip update
android.skip_update = False

# Add java options to handle build issues
android.add_java_jar = libs/android-support-v4.jar

# Gradle dependencies
android.gradle_dependencies = 

# Enable debugging
android.debug = 1

# Optimize APK
android.release_artifact = apk