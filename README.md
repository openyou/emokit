Emokit
======

Reverse engineering and original code written by

* Cody Brocious (http://github.com/daeken)
* Kyle Machulis (http://github.com/qdot)

Contributions by

* Severin Lemaignan - Base C Library and mcrypt functionality
* Sharif Olorin  (http://github.com/fractalcat) - hidapi support
* Bill Schumacher (http://github.com/bschumacher) - Fixed the Python library

Description
===========

Emokit is a set of language for user space access to the raw stream
data from the Emotiv EPOC headset. Note that this will not give you
processed data (i.e. anything available in the Emo Suites in the
software), just the raw sensor data.

The C library is backed by hidapi, and should work on any platform
that hidapi also works on.

Information
===========

FAQ (READ BEFORE FILING ISSUES): https://github.com/openyou/emokit/blob/master/FAQ.md

If you have a problem not covered in the FAQ, file it as an
issue on the github project.

PLEASE DO NOT EMAIL OR OTHERWISE CONTACT THE DEVELOPERS DIRECTLY.
Seriously. I'm sick of email and random facebook friendings asking for
help. What happens on the project stays on the project.

Issues: http://github.com/openyou/emokit/issues

If you are using the Python library and a research headset you may have
to change the is_research variable in emotiv.py's setup_crypto function.

Required Libraries
==================

Python
------

* pycrypto - https://www.dlitz.net/software/pycrypto/
* gevent - http://gevent.org

Windows
* pywinusb (Windows Only) - https://pypi.python.org/pypi/pywinusb/

Linux / OS X
* hidapi - http://www.signal11.us/oss/hidapi/
* pyhidapi - https://github.com/NF6X/pyhidapi


C Language
----------

* CMake - http://www.cmake.org
* libmcrypt - https://sourceforge.net/projects/mcrypt/
* hidapi - http://www.signal11.us/oss/hidapi/

Usage
=====

C library
---------

See epocd.c example

Python library
--------------

  Code:
  
    import emotiv
    import platform
    if platform.system() == "Windows":
        import socket
    import gevent

    if __name__ == "__main__":
      headset = emotiv.Emotiv()    
      gevent.spawn(headset.setup)
      gevent.sleep(0)
      try:
        while True:
          packet = headset.dequeue()
          print packet.gyro_x, packet.gyro_y
          gevent.sleep(0)
      except KeyboardInterrupt:
        headset.close()
      finally:
        headset.close()


Bindings
========

Go: https://github.com/fractalcat/emogo

Platform Specifics Issues
=========================

Linux
-----

Due to the way hidapi works, the linux version of emokit can run using
either hidraw calls or libusb. These will require different udev rules
for each. We've tried to cover both (as based on hidapi's example udev
file), but your mileage may vary. If you have problems, please post
them to the github issues page (http://github.com/openyou/emokit/issues).

Your kernel may not support /dev/hidraw devices by default, such as an RPi.
To fix that re-comiple your kernel with /dev/hidraw support

OS X
----
Recent OS versions no longer allow usb devices to become unclaimed by the kernel.
You must use a HIDAPI library.

The render.py file uses pygame, visit http://pygame.org/wiki/MacCompile
Do not export the architecture compiler flags for recent 64bit versions of OS X.


Credits - Cody
==============

Huge thanks to everyone who donated to the fund drive that got the
hardware into my hands to build this.

Thanks to Bryan Bishop and the other guys in #hplusroadmap on Freenode
for your help and support.

And as always, thanks to my friends and family for supporting me and
suffering through my obsession of the week.

Credits - Kyle
==============

Kyle would like to thank Cody for doing the hard part. 

He would also like to thank emotiv for putting emo on the front of
everything because it's god damn hilarious. I mean, really, Emo
Suites? Saddest hotel EVER.

# Frequently asked questions

 - *What unit is the data I'm getting back in? How do I get volts out of
 it?*

 One least-significant-bit of the fourteen-bit value you get back is
 0.51 microvolts. See the
 [specification](http://emotiv.com/upload/manual/EPOCSpecifications.pdf)
 for more details.