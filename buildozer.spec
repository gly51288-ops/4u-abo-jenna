[app]
title = 4U Abo Jenna
package.name = abojenna
package.domain = org.gly51288

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,mp3,ogg,ttf,otf,atlas,kv,json
source.exclude_dirs = bin,build,.buildozer
source.exclude_patterns = *.pyc,__pycache__/*,README.md

version = 0.1

requirements = python3,pygame

orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
