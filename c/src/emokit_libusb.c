/* Copyright (c) 2011-2012, Kyle Machulis <kyle@nonpolynomial.com>
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include "emokit/emokit.h"
#include <stdio.h>
#include <stdlib.h>

#define EMOKIT_USB_INTERFACE	0

emokit_device* emokit_create()
{
	emokit_device* s = (emokit_device*)malloc(sizeof(emokit_device));
	s->_is_open = 0;
	s->_is_inited = 0;
	if(libusb_init(&s->_context) < 0)
	{
		return NULL;
	}
	s->_is_inited = 1;	
	return s;
}

int emokit_get_count(emokit_device* s, int device_vid, int device_pid)
{
	struct libusb_device **devs;
	struct libusb_device *found = NULL;
	struct libusb_device *dev;
	size_t i = 0;
	int count = 0;

	if (!s->_is_inited)
	{
		return E_EMOKIT_NOT_INITED;
	}
	
	if (libusb_get_device_list(s->_context, &devs) < 0)
	{
		return E_EMOKIT_DRIVER_ERROR;
	}

	while ((dev = devs[i++]) != NULL)
	{
		struct libusb_device_descriptor desc;
		int dev_error_code;
		dev_error_code = libusb_get_device_descriptor(dev, &desc);
		if (dev_error_code < 0)
		{
			break;
		}
		if (desc.idVendor == device_vid && desc.idProduct == device_pid)
		{
			++count;
		}
	}

	libusb_free_device_list(devs, 1);
	return count;
}

int emokit_open(emokit_device* s, int device_vid, int device_pid, unsigned int device_index)
{
	int ret;
	struct libusb_device **devs;
	struct libusb_device *found = NULL;
	struct libusb_device *dev;
	size_t i = 0;
	int count = 0;
	int device_error_code = 0;

	if (!s->_is_inited)
	{
		return E_EMOKIT_NOT_INITED;
	}

	if ((device_error_code = libusb_get_device_list(s->_context, &devs)) < 0)
	{
		return E_EMOKIT_DRIVER_ERROR;
	}

	struct libusb_device_descriptor desc;
	while ((dev = devs[i++]) != NULL)
	{
		device_error_code = libusb_get_device_descriptor(dev, &desc);
		if (device_error_code < 0)
		{
			libusb_free_device_list(devs, 1);
			return E_EMOKIT_NOT_INITED;
		}
		if (desc.idVendor == device_vid && desc.idProduct == device_pid)
		{
			if(count == device_index)
			{
				found = dev;
				break;
			}
			++count;
		}
	}

	if (found)
	{		
		device_error_code = libusb_open(found, &s->_device);
		if (device_error_code < 0)
		{
			libusb_free_device_list(devs, 1);
			return E_EMOKIT_NOT_INITED;
		}
		libusb_get_device_descriptor(found, &desc);
		// Why does this want 17 bytes?
		libusb_get_string_descriptor_ascii(s->_device, desc.iSerialNumber, s->serial, 17);
	}
	else
	{
		return E_EMOKIT_NOT_INITED;		
	}
	s->_is_open = 1;

	if(libusb_kernel_driver_active(s->_device, 0))
	{
		printf("Detach 0\n");
		libusb_detach_kernel_driver(s->_device, 0);
	}
	ret = libusb_claim_interface(s->_device, 0);

	if (ret != 0) printf("ACK!\n");

	if(libusb_kernel_driver_active(s->_device, 1))
	{
		printf("Detach 4\n");		
		libusb_detach_kernel_driver(s->_device, 1);
	}
	ret = libusb_claim_interface(s->_device, 1);
	printf("Done %d\n", ret);

	emokit_init_crypto(s);
	return ret;
}

int emokit_close(emokit_device* s)
{
	if(!s->_is_open)
	{
		return E_EMOKIT_NOT_OPENED;
	}
	if (libusb_release_interface(s->_device, 0) < 0)
	{
		return E_EMOKIT_NOT_INITED;				
	}
	libusb_close(s->_device);
	s->_is_open = 0;
	return 0;
}

int emokit_read_data(emokit_device* dev)
{
	int trans;
	int ret = libusb_interrupt_transfer(dev->_device, EMOKIT_IN_ENDPT, dev->raw_frame, 32, &trans, 1000);
	return trans;
}

