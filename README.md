Usage
=====

Python library
--------------

    import emotiv
    headset = emotiv.Emotiv()
    try:
	    while True:
	    	for packet in headset.dequeue():
	    		print packet.gyroX, packet.gyroY
	  finally:
	    headset.close()

Credits
=======

Huge thanks to everyone who donated to the fund drive that got the hardware into my hands to build this.
Thanks to Bryan Bishop and the other guys in #hplusroadmap on Freenode for your help and support.
And as always, thanks to my friends and family for supporting me and suffering through my obsession of the week.
