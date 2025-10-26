[app]
title = Assistant 2.0
package.name = myapp.assistant.new
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3==3.8.5,kivy,kivymd,pyjnius

[buildozer]
log_level = 2

[android]
api = 31
minapi = 21
ndk = 23b


# buildozer.spec
p4a.branch = develop
