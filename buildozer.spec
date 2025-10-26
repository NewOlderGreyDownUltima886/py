[app]
title = Ассистент
package.name = assistant
package.domain = ru.assistant

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[android]
api = 21
minapi = 21
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.orientation = portrait
