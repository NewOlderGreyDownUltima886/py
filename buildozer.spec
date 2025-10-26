[app]
title = Ассистент 2.0
package.name = assistant
package.domain = ru.assistant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi,android

[buildozer]
log_level = 2

[android]
api = 21
minapi = 21
ndk = 25b
sdk = 33
android.accept_sdk_license = True
android.allow_backup = True
android.fullscreen = 0
android.orientation = portrait
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE


[android:activity]
android.launch_mode = singleTop

android.gradle_dependencies = 'implementation 'com.squareup.okhttp3:okhttp:4.9.3''
