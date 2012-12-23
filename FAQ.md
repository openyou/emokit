Emokit FAQ
==========

* What data does emokit give me?

The raw channels of the headset

Battery power of the headset (in development at time of FAQ writing)

Signal quality of each connection on the headset (in development at time of FAQ writing)

* What data does emokit not give me?

Processed data that can tell you moods or muscles or whatever.

Basically, if you aren't up to doing a bit of DSP and aren't really
educated in mathematics and neuroscience, you should use emokit under
another library that will do the geekery for you. We publish emokit as
a low level access tool, nothing more.

* Does emokit work with all emotiv headsets?

As far as we know, yes. If it doesn't work with yours, file an issue
on the github project (http://github.com/openyou/emokit/issues)

* I heard you need to know your key or something?

That doesn't apply anymore. Emokit should work with all headsets and
dongles. If it doesn't, file an issue (http://github.com/openyou/emokit/issues).

* So I really don't need to know my key or whatever now?

You shouldn't. It should "just work". So please stop asking.

* OPTIONAL READING: The history of the key generation, and why you used to need keys

When emokit first came out (For more information on this, check out
Announcement.md in the doc directory), we only knew part of how the
encryption worked, mainly because Daeken finished the first round,
qDot took things over, and then neither of them had time to do
anything for a while. So there was a lot of news that went around of
"only certain headsets/keys work", so on and so forth.

We managed to get lucky with the method for a while, because Emotiv
was reusing keys on USB dongles, so one key would work for many
headsets. Once Emotiv learned of this, they just had to switch out the
firmware flashing on their keys, and emokit no longer worked.

In late 2011, Daeken finished the key generation code, which means
emokit should now work for any USB key. Note that the encryption
happens on the USB KEY, not the headset. So it's actually tied to
whatever you have plugged in regardless of the headset.

