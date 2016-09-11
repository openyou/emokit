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
  
    import emotiv

    if __name__ == "__main__":
      with emotiv.Emotiv() as headset:
          while True:
            packet = headset.dequeue()
            if packet is not None:
                print("Gyro - X:{x_position} Y:{y_position}".format(x_position=packet.sensors['X']['value'],
                                                                    y_position=packet.sensors['Y']['value']))



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
 Y Reading: 0 Quality: 0
 F3 Reading: 316 Quality: 24
 F4 Reading: 779 Quality: 16
 P7 Reading: 189 Quality: 0
 FC6 Reading: 925 Quality: 24
 F7 Reading: 80 Quality: 0
 F8 Reading: 1037 Quality: 8
 T7 Reading: 345 Quality: 16
 P8 Reading: -92 Quality: 16
 FC5 Reading: 1113 Quality: 16
 AF4 Reading: 476 Quality: 0
 Unknown Reading: 82 Quality: 8
 T8 Reading: 636 Quality: 16
 X Reading: 1 Quality: 0
 Z Reading: ? Quality: 0
 O2 Reading: 216 Quality: 0
 O1 Reading: -39 Quality: 24
 AF3 Reading: 100 Quality: 24
 Battery: 0
