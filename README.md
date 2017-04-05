Emokit
======

Reverse engineering and original code written by

* Cody Brocious (http://github.com/daeken)
* Kyle Machulis (http://github.com/qdot)

Contributions by

* Severin Lemaignan - Base C Library and mcrypt functionality
* Sharif Olorin  (http://github.com/fractalcat) - hidapi support
* Bill Schumacher (http://github.com/bschumacher) - Fixed the Python library

Headset Support
===============

Supported: Epoc, Epoc+(Pre-2016, limited gyro sensors)
Unsupported: Epoc+(2016+), other models.

Description
===========

Emokit is a set of language for user space access to the raw stream
data from the Emotiv EPOC headset. Note that this will not give you
processed data (i.e. anything available in the Emo Suites in the
software), just the raw sensor data.

C Library
=========

Please note that the python and C libraries are now in different
repos. If you would like to use the C version of emokit, the repo
is at

http://www.github.com/openyou/emokit-c

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

2.x
* future - pip install future
  
Windows
* pywinusb - https://pypi.python.org/pypi/pywinusb/

Linux / OS X
* hidapi - http://www.signal11.us/oss/hidapi/
* pyhidapi - https://github.com/NF6X/pyhidapi

Running tests
* pytest - http://doc.pytest.org/en/latest/

You should be able to install emokit and the required python libraries using:  

pip install emokit

OR

python setup.py install

hidapi will still need to be installed manually on Linux and OS X.


Usage
=====

Python library
--------------

  Code:

    # -*- coding: utf-8 -*-
    # This is an example of popping a packet from the Emotiv class's packet queue


    import time

    from emokit.emotiv import Emotiv

    if __name__ == "__main__":
        with Emotiv(display_output=True, verbose=True) as headset:
            while True:
                packet = headset.dequeue()
                if packet is not None:
                   pass
                time.sleep(0.001)


Bindings
========

Go: https://github.com/fractalcat/emogo


Running Unit Tests
==================

From the python directory in your terminal type:

  Code:  

    python -m pytest tests/
      

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
 for more details. (Broken Link)
 
 - *What should my output look like?*
 
 Idling, not on someone's head it should look something like this:  

Emokit - v0.0.8 SN: ActualSerialNumberHere  Old Model: False
+========================================================+
| Sensor |   Value  | Quality  | Quality L1 | Quality L2 |
+--------+----------+----------+------------+------------+
|   F3   |   292    |    24    |  Nothing   |  Nothing   |
|   FC5  |   1069   |    0     |  Nothing   |  Nothing   |
|   AF3  |   110    |    8     |  Nothing   |  Nothing   |
|   F7   |    63    |    24    |  Nothing   |  Nothing   |
|   T7   |   322    |    8     |  Nothing   |  Nothing   |
|   P7   |   166    |    0     |  Nothing   |  Nothing   |
|   O1   |   -62    |    24    |  Nothing   |  Nothing   |
|   O2   |   235    |    24    |  Nothing   |  Nothing   |
|   P8   |   -63    |    24    |  Nothing   |  Nothing   |
|   T8   |   626    |    16    |  Nothing   |  Nothing   |
|   F8   |   1045   |    16    |  Nothing   |  Nothing   |
|   AF4  |   578    |    8     |  Nothing   |  Nothing   |
|   FC6  |   973    |    16    |  Nothing   |  Nothing   |
|   F4   |   780    |    8     |  Nothing   |  Nothing   |
|   X    |    2     |   N/A    |    N/A     |    N/A     |
|   Y    |    1     |   N/A    |    N/A     |    N/A     |
|   Z    |    ?     |   N/A    |    N/A     |    N/A     |
|  Batt  |    46    |   N/A    |    N/A     |    N/A     |
+--------+----------+----------+------------+------------+
|Packets Received:   452    |  Packets Processed:   447  |
|   Sampling Rate:    2     |        Crypto Rate:    0   |
+========================================================+
