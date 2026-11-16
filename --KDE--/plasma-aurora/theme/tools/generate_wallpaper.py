#!/usr/bin/env python3
"""Generate Aurora PNG wallpaper and KDE theme previews using only Python stdlib."""
import math
import struct
import sys
import zlib
from pathlib import Path

def chunk(tag, payload):
    return (struct.pack(">I", len(payload)) + tag + payload +
            struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff))

def render(filename, width, height):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    compressor = zlib.compressobj(7)
    data = bytearray()
    horizontal = [x / (width - 1) for x in range(width)]
    for y in range(height):
        v = y / (height - 1)
        scanline = bytearray(b"\x00")
        for u in horizontal:
            axis = 0.48 - 0.105 * u - 0.065 * math.sin(5.4 * u + 0.3)
            distance = (v - axis) / 0.115
            glow = math.exp(-distance * distance)
            soft = math.exp(-((v - axis - 0.065) / 0.24) ** 2) * 0.38
            cyan = max(0.0, 1.0 - u * 1.15)
            violet = max(0.0, (u - 0.31) / 0.65)
            backdrop = 0.4 * (1.0 - v)
            r = 11 + 11 * backdrop + 31 * soft + (20 + 78 * violet) * glow
            g = 12 + 10 * backdrop + 32 * cyan * soft + (60 * cyan + 13) * glow
            b = 35 + 28 * backdrop + 50 * soft + 108 * glow
            scanline.extend((min(255, int(r)), min(255, int(g)), min(255, int(b))))
        data.extend(compressor.compress(scanline))
    data.extend(compressor.flush())
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    png.extend(chunk(b"IDAT", data))
    png.extend(chunk(b"IEND", b""))
    filename.write_bytes(png)

def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: generate_wallpaper.py FULL_PNG SCREENSHOT_PNG PREVIEW_PNG")
    render(sys.argv[1], 2560, 1440)
    render(sys.argv[2], 960, 540)
    render(sys.argv[3], 960, 540)

if __name__ == "__main__":
    main()
