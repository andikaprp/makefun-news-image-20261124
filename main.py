#!/usr/bin/env python3
"""Stdlib-only copier: copies entry.png to /output/entry.png."""
import os, shutil

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(src, "/output/entry.png")

if __name__ == "__main__":
    main()
