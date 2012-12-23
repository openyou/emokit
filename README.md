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

FAQ (READ BEFORE FILING ISSUES): http://github.com/openyou/emokit/FAQ.md

If you have a problem not covered in the FAQ, file it as an
issue on the github project.

PLEASE DO NOT EMAIL OR OTHERWISE CONTACT THE DEVELOPERS DIRECTLY.
Seriously. I'm sick of email and random facebook friendings asking for
help. What happens on the project stays on the project.

Issues: http://github.com/openyou/emokit/issues

If you are using the Python library and a research headset you may have to change the type in emotiv.py's setupCrypto function. 

Required Libraries
==================

Python
------

* pywinhid (Windows Only) - http://code.google.com/p/pywinusb/
* pyusb (OS X, Optional for Linux) - http://sourceforge.net/projects/pyusb/
* pycrypto - https://www.dlitz.net/software/pycrypto/
* gevent - http://gevent.org
* realpath - http://?   sudo apt-get install realpath

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
    import gevent

    if __name__ == "__main__":
      headset = emotiv.Emotiv()    
      gevent.spawn(headset.setup)
      gevent.sleep(1)
      try:
        while True:
          packet = headset.dequeue()
          print packet.gyroX, packet.gyroY
          gevent.sleep(0)
      except KeyboardInterrupt:
        headset.close()
      finally:
        headset.close()

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
