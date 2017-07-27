# Object Tracking

Video demonstration: https://www.youtube.com/watch?v=Cp8_2hkGA6s

![look](https://github.com/danielsnider/object-tracking/blob/master/Object_Tracking.png)

Camera frames are (A) processed using OpenCV (background subtraction, noise reduction, and tracking) on one or more Raspberry Pi's then (B) published with metadata over AMQP to a central web server then (C) streamed over a websocket to a browser for viewing and real-time parameter tweaking. Parameter changes are relayed back to all connected Raspberry Pi's.


