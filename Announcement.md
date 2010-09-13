Intro
=====

I've been interested in the [Emotiv EPOC](http://emotiv.com/) headset for a while; a $300 14-sensor EEG.  It's intended for gaming, but it's quite high quality.  There's a research SDK available for $750, but it's Windows-only and totally proprietary.  I decided to hack it, and open the consumer headset up to development.  Thanks to [donations](http://pledgie.com/campaigns/12906) I got some hardware in hand this weekend.

I'm happy to announce the Emokit project, an open source interface to the EPOC.  The goal is to open it up to development and enable new products and research.  For the first time, we have access to a high-quality EEG for $300 -- this is huge.

Code
====

The code is available on github on the [daeken/Emokit](http://github.com/daeken/Emokit) repository.  There's a Python library for interacting with the EPOC, as well as a renderer that will graph the sensor data.

![Graph in debug mode](http://i53.tinypic.com/34yyy47.jpg)

Where things are right now
==========================

You can access raw EEG data from the Emotiv EPOC on Windows, Linux, and OS X from Python.  While it's not known exactly which sensors are which in the data (read below for more info), it's close to being useful already.  Word of warning: this project is less than 48 hours old (I just got hardware in my hands Saturday night) and has only been run by me on Windows due to a dead Linux box.  It's very much alpha quality right now -- don't trust it.

How it happened
===============

The first step was to figure out how exactly the PC communicates with it.  This part was straightforward; it's a USB device with VID=21A1, PID=0001 (note: from walking through the device enum code in the EDK, it seems that PID=0002 might be the development headset, but that's totally unverified).  It presents two HID interfaces, "EPOC BCI" and "Brain Waves".  Reading data off the "Brain Waves" interface gives you reports of 32 bytes at a time; "EPOC BCI" I'm unsure about.

Next step was to read some data off the wire and figure out what's going on.  I utilized the pywinusb.hid library for this.  It was immediately apparent that it's encrypted, so figuring out what the crypto was became the top priority.  This took a couple hours due to a few red herrings and failed approaches, but here's what it boiled down to:

- Throw EmotivControlPanel.exe into IDA.
- Throw EmotivControlPanel.exe into PeID and run the Krypto Analyzer plugin on it.
- You'll see a Rijndael S-Box (used for AES encryption and key schedule initialization) come up from KAnal.
- Using IDA, go to the S-Box address.
- You'll see a single function that references the S-Box -- this is the key initialization code (*not* encryption, as I originally thought).
- Use a debugger (I used the debugger built into IDA for simplicity's sake) and attach to the beginning of the key init function.
- You'll see two arguments: a 16-byte key and an integer containing `16`.

So that you don't have to do that yourself, here's the key: 31003554381037423100354838003750 or `1\x005T8\x107B1\x005H8\x007P`.  Given that, decrypting the data is trivial: it's simply 128-bit AES in ECB mode, block size of 16 bytes.

The first byte of each report is a counter that goes from 0-127 then to 233, then cycles back to 0.  Once this was determined, I figured out the gyro data.  To do that, I broke out pygame and wrote a simple app that drew a rectangle at the X and Y coords coming from two bytes of the records.  I pretty quickly figured out that the X coord from the gyro is byte 29 and the Y coord is byte 30.  The EPOC has some sort of logic in it to reset the gyro baseline levels, but I'm not sure on the details there; the baseline I'm seeing generally (not perfect) is roughly 102 for X and 204 for Y.  This lets you get control from the gyro fairly easy.

That accounts for 3 bytes of the packet, but we have 14 sensors.  If you assume that each sensor is represented by 2 bytes of data, that gives us 28 bytes for sensor data.  32 - 28 == 4, so what's the extra byte?  Looking at byte 15, it's pretty clear that it's (almost) always zero -- the only time it's non-zero is the very first report from the device.  I have absolutely no idea what this is.

From here, all we have is data from the sensors.  Another quick script with pygame and boom, we have a graph renderer for this data.

However, here's where it gets tough.  Figuring out which bytes correspond to which sensors is difficult, because effectively all the signal processing and filtering happens on the PC side, meaning it's not in this library yet.  Figuring out the high bytes (which are less noisy and change less frequently) isn't terribly difficult, and I've identified a few of them, but there's a lot of work to be done still.

What needs to be done
=====================

Reversing-wise:

- Determine which bytes correspond to which signals -- I'm sure someone more knowledgable than myself can do this no problem
- Figure out how the sensor quality is transmitted -- according to some data on the research SDK, there's 4 bits per sensor that give you the signal quality (0=none, 1=very poor, 2=poor, 3=decent, 4=good, 5=very good)
- Figure out how to read the battery meter

Emokit-wise:

- Linux and OS X support haven't been tested at all, but they should be good to go
- Build a C library for working with the EPOC
- Build an acquisition module for [OpenViBE](http://openvibe.inria.fr/)

Get involved
================

Contact us
----------

I've started the [#emokit channel on Freenode](irc://irc.freenode.net/emokit) and I'm idling there (nick=Daeken).

How you can help
----------------

I'm about to get started on an acquisition module for OpenViBE, but someone more knowledgable than myself could probably do this far more quickly.  However, the reversing side of things -- particularly figuring out the sensor bytes -- would be much more useful.

Summary
=======

I hope that the Emokit project will open new research that was never possible before, and I can't wait to see what people do with this.  Let me know if you have any questions or comments.

Happy Hacking,  
- Cody Brocious (Daeken)
