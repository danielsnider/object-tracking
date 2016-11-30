# About

- Code is fork of: https://github.com/phoboslab/jsmpeg
- Guide: http://phoboslab.org/log/2013/09/html5-live-video-streaming-via-websockets

# Setup

```bash
# install nodejs, npm, ffmpeg, chrome
npm install
cd webserver
node stream-server.js yourpassword
ffmpeg -s 640x480 -f video4linux2 -i /dev/video0 -f mpeg1video -b 800k -r 30 http://127.0.0.1:8082/yourpassword/640/480/
google-chrome stream-example.html
```

# Notes

- Latency is very fast
- Works like a charm
