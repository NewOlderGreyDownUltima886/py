[app]
title = Ассистент 2.0
package.name = assistant
package.domain = ru.assistant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt

version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 33

# Разрешения
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Особые настройки
android.accept_sdk_license = True

[android:meta-data]
android.allow_backup = true

[android:activity]
android.launch_mode = singleTop


