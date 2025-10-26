[app]
title = Ассистент 2.0
package.name = assistant
package.domain = ru.assistant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
icon.filename = %(source.dir)s/icon.png

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
api = 21
minapi = 21
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.orientation = portrait


# Добавьте эти опции
android.api = 33
android.minapi = 21

# Добавьте эти intent filters для работы с файлами
android.manifest.intent_filters = <intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:mimeType="text/plain" />
</intent-filter>
<intent-filter>
    <action android:name="android.intent.action.OPEN_DOCUMENT" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="*/*" />
</intent-filter>
