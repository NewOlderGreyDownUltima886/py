[app]
title = My App
package.name = myapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json

version = 0.1
requirements = python3==3.8.5,kivy,kivymd

orientation = portrait

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
ndk = 23b

# Указываем конкретную версию python-for-android
p4a.branch = develop

[python-for-android]
recipe.cython = cython==0.29.36
