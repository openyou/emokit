/*
 * Generic function file for EPOC EEG User Space Driver - libusb version
 *
 */


#include "libepoc.h"
#include <stdlib.h>

#define EPOC_USB_INTERFACE	0

epoc_device* epoc_create()
{
	epoc_device* s = (epoc_device*)malloc(sizeof(epoc_device));
	s->_is_open = 0;
	s->_is_inited = 0;
	if(libusb_init(&s->_context) < 0)
	{
		return NULL;
	}
	s->_is_inited = 1;	
	return s;
}

int epoc_get_count(epoc_device* s, int device_vid, int device_pid)
{
	struct libusb_device **devs;
	struct libusb_device *found = NULL;
	struct libusb_device *dev;
	size_t i = 0;
	int count = 0;

	if (!s->_is_inited)
	{
		return E_NPUTIL_NOT_INITED;
	}
	
	if (libusb_get_device_list(s->_context, &devs) < 0)
	{
		return E_NPUTIL_DRIVER_ERROR;
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

int epoc_open(epoc_device* s, int device_vid, int device_pid, unsigned int device_index)
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
		return E_NPUTIL_NOT_INITED;
	}

	if ((device_error_code = libusb_get_device_list(s->_context, &devs)) < 0)
	{
		return E_NPUTIL_DRIVER_ERROR;
	}

	while ((dev = devs[i++]) != NULL)
	{
		struct libusb_device_descriptor desc;
		device_error_code = libusb_get_device_descriptor(dev, &desc);
		if (device_error_code < 0)
		{
			libusb_free_device_list(devs, 1);
			return E_NPUTIL_NOT_INITED;
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
			return E_NPUTIL_NOT_INITED;
		}
	}
	else
	{
		return E_NPUTIL_NOT_INITED;		
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
	return ret;
}

int epoc_close(epoc_device* s)
{
	if(!s->_is_open)
	{
		return E_NPUTIL_NOT_OPENED;
	}
	if (libusb_release_interface(s->_device, 0) < 0)
	{
		return E_NPUTIL_NOT_INITED;				
	}
	libusb_close(s->_device);
	s->_is_open = 0;
	return 0;
}

void epoc_delete(epoc_device* dev)
{
	free(dev);
}

int epoc_read_data(epoc_device* dev, uint8_t* input_report)
{
	int trans;
	int ret = libusb_interrupt_transfer(dev->_device, EPOC_IN_ENDPT, input_report, 32, &trans, 1000);
	return trans;
}

