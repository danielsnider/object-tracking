#!/bin/bash
# MPEG1
./pttranscoder/pttranscoder.py | ffmpeg -f rawvideo -pix_fmt bgr24 -s 640x480 -i - -f mpeg1video -b 800k -r 30 http://127.0.0.1:8082/yourpassword/640/480/

# x264
# ffmpeg -y -i sourceFile -r 30000/1001 -b:a 2M -bt 4M -vcodec libx264 -pass 1 -coder 0 -bf 0 -flags -loop -wpredp 0 -an targetFile.mp4
# https://github.com/mbebenita/broadway