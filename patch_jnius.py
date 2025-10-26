#!/usr/bin/env python3
import os
import fileinput

def patch_jnius_file():
    file_path = ".buildozer/android/platform/python-for-android/pythonforandroid/recipes/jnius/jnius/jnius_utils.pxi"
    
    if os.path.exists(file_path):
        with fileinput.FileInput(file_path, inplace=True, backup='.bak') as file:
            for line in file:
                # Заменяем long на int для Python 3
                if 'isinstance(arg, long)' in line:
                    line = line.replace('isinstance(arg, long)', 'isinstance(arg, int)')
                print(line, end='')
        print(f"Patched {file_path}")
    else:
        print(f"File {file_path} not found")

if __name__ == "__main__":
    patch_jnius_file()
