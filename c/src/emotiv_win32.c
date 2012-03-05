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
#include <stdlib.h>
#include <api/setupapi.h>
#include <api/hidsdi.h>
#include <stdio.h>

#define EMOKIT_USB_INTERFACE	0


//Application global variables
DWORD								ActualBytesRead;
DWORD								BytesRead;
HIDP_CAPS							Capabilities;
DWORD								cbBytesRead;
PSP_DEVICE_INTERFACE_DETAIL_DATA	detailData;
DWORD								dwError;
char								FeatureReport[256];
HANDLE								hEventObject;
HANDLE								hDevInfo;
GUID								HidGuid;
OVERLAPPED							HIDOverlapped;
char								InputReport[256];
ULONG								Length;
LPOVERLAPPED						lpOverLap;
BOOL								MyDeviceDetected		 = FALSE;
TCHAR*								MyDevicePathName;
DWORD								NumberOfBytesRead;
char								OutputReport[256];
DWORD								ReportType;
ULONG								Required;
TCHAR*								ValueToDisplay;

void GetDeviceCapabilities(HANDLE DeviceHandle)
{
	//Get the Capabilities structure for the device.

	PHIDP_PREPARSED_DATA	PreparsedData;

	/*
	  API function: HidD_GetPreparsedData
	  Returns: a pointer to a buffer containing the information about the device's capabilities.
	  Requires: A handle returned by CreateFile.
	  There's no need to access the buffer directly,
	  but HidP_GetCaps and other API functions require a pointer to the buffer.
	*/

	HidD_GetPreparsedData
		(DeviceHandle,
		 &PreparsedData);

	/*
	  API function: HidP_GetCaps
	  Learn the device's capabilities.
	  For standard devices such as joysticks, you can find out the specific
	  capabilities of the device.
	  For a custom device, the software will probably know what the device is capable of,
	  and the call only verifies the information.
	  Requires: the pointer to the buffer returned by HidD_GetPreparsedData.
	  Returns: a Capabilities structure containing the information.
	*/

	HidP_GetCaps
		(PreparsedData,
		 &Capabilities);

	HidD_FreePreparsedData(PreparsedData);
}

int emokit_open_win32(emokit_device* dev, int VID, int PID, unsigned int device_index, int get_count)
{
	//Use a series of API calls to find a HID with a specified Vendor IF and Product ID.

	HIDD_ATTRIBUTES						Attributes;
	SP_DEVICE_INTERFACE_DATA			devInfoData;
	BOOL								LastDevice = FALSE;
	int									MemberIndex = 0;
	LONG								Result;
	int									device_count = 0;

	Length = 0;
	detailData = NULL;
	dev->_dev = NULL;

	/*
	  API function: HidD_GetHidGuid
	  Get the GUID for all system HIDs.
	  Returns: the GUID in HidGuid.
	*/

	HidD_GetHidGuid(&HidGuid);

	/*
	  API function: SetupDiGetClassDevs
	  Returns: a handle to a device information set for all installed devices.
	  Requires: the GUID returned by GetHidGuid.
	*/

	hDevInfo=SetupDiGetClassDevs
		(&HidGuid,
		 NULL,
		 NULL,
		 DIGCF_PRESENT|DIGCF_INTERFACEDEVICE);

	devInfoData.cbSize = sizeof(devInfoData);

	//Step through the available devices looking for the one we want.
	//Quit on detecting the desired device or checking all available devices without success.

	MemberIndex = 0;
	LastDevice = FALSE;

	do
	{
		/*
		  API function: SetupDiEnumDeviceInterfaces
		  On return, MyDeviceInterfaceData contains the handle to a
		  SP_DEVICE_INTERFACE_DATA structure for a detected device.
		  Requires:
		  The DeviceInfoSet returned in SetupDiGetClassDevs.
		  The HidGuid returned in GetHidGuid.
		  An index to specify a device.
		*/

		Result=SetupDiEnumDeviceInterfaces
			(hDevInfo,
			 0,
			 &HidGuid,
			 MemberIndex,
			 &devInfoData);

		if (Result != 0)
		{
			//A device has been detected, so get more information about it.

			/*
			  API function: SetupDiGetDeviceInterfaceDetail
			  Returns: an SP_DEVICE_INTERFACE_DETAIL_DATA structure
			  containing information about a device.
			  To retrieve the information, call this function twice.
			  The first time returns the size of the structure in Length.
			  The second time returns a pointer to the data in DeviceInfoSet.
			  Requires:
			  A DeviceInfoSet returned by SetupDiGetClassDevs
			  The SP_DEVICE_INTERFACE_DATA structure returned by SetupDiEnumDeviceInterfaces.

			  The final parameter is an optional pointer to an SP_DEV_INFO_DATA structure.
			  This application doesn't retrieve or use the structure.
			  If retrieving the structure, set
			  MyDeviceInfoData.cbSize = length of MyDeviceInfoData.
			  and pass the structure's address.
			*/

			//Get the Length value.
			//The call will return with a "buffer too small" error which can be ignored.

			Result = SetupDiGetDeviceInterfaceDetail
				(hDevInfo,
				 &devInfoData,
				 NULL,
				 0,
				 &Length,
				 NULL);

			//Allocate memory for the hDevInfo structure, using the returned Length.

 			detailData = (PSP_DEVICE_INTERFACE_DETAIL_DATA)malloc(Length);

			//Set cbSize in the detailData structure.

			detailData -> cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);

			//Call the function again, this time passing it the returned buffer size.

			Result = SetupDiGetDeviceInterfaceDetail
				(hDevInfo,
				 &devInfoData,
				 detailData,
				 Length,
				 &Required,
				 NULL);

			// Open a handle to the device.
			// To enable retrieving information about a system mouse or keyboard,
			// don't request Read or Write access for this handle.

			/*
			  API function: CreateFile
			  Returns: a handle that enables reading and writing to the device.
			  Requires:
			  The DevicePath in the detailData structure
			  returned by SetupDiGetDeviceInterfaceDetail.
			*/

			
			dev->_dev =CreateFile
				(detailData->DevicePath,
				 GENERIC_READ | GENERIC_WRITE,
				 FILE_SHARE_READ|FILE_SHARE_WRITE,
				 (LPSECURITY_ATTRIBUTES)NULL,
				 OPEN_EXISTING,
				 0,
				 NULL);

			/*
			  API function: HidD_GetAttributes
			  Requests information from the device.
			  Requires: the handle returned by CreateFile.
			  Returns: a HIDD_ATTRIBUTES structure containing
			  the Vendor ID, Product ID, and Product Version Number.
			  Use this information to decide if the detected device is
			  the one we're looking for.
			*/

			//Set the Size to the number of bytes in the structure.

			Attributes.Size = sizeof(Attributes);

			Result = HidD_GetAttributes
				(dev->_dev,
				 &Attributes);

			//Is it the desired device?

			MyDeviceDetected = FALSE;

			if ((Attributes.VendorID == VID && Attributes.ProductID == PID))
			{
				if(get_count || device_count != device_index)
				{
					CloseHandle(dev->_dev);
				}
				else if (device_count  == device_index)
				{
					MyDeviceDetected = TRUE;
					MyDevicePathName = detailData->DevicePath;
					GetDeviceCapabilities(dev->_dev);
					break;
				}
				++device_count;
			}
			else
			{
				CloseHandle(dev->_dev);
			}
			free(detailData);
		}  //if (Result != 0)

		else
		{
			LastDevice=TRUE;
		}
		//If we haven't found the device yet, and haven't tried every available device,
		//try the next one.
		MemberIndex = MemberIndex + 1;
	}
	while (!LastDevice);
	SetupDiDestroyDeviceInfoList(hDevInfo);
	if(get_count) return device_count;
	if(MyDeviceDetected) return 0;
	return -1;
}

EMOKIT_DECLSPEC int emokit_get_count(emokit_device* dev,int device_vid, int device_pid)
{
	return emokit_open_win32(dev, device_vid, device_pid, 0, 1);
}

EMOKIT_DECLSPEC int emokit_open(emokit_device* dev, int device_vid, int device_pid, unsigned int device_index)
{
	return emokit_open_win32(dev, device_vid, device_pid, device_index, 0);
}

EMOKIT_DECLSPEC int emokit_close(emokit_device* dev)
{
	CloseHandle(dev->_dev);
	return 0;
}

EMOKIT_DECLSPEC int emokit_read_data(emokit_device* dev)
{
	int Result;
	char read[33];
	Result = ReadFile
		(dev->_dev,
		 read,
		 Capabilities.InputReportByteLength,
		 &NumberOfBytesRead,
		 NULL);
	memcpy(dev->raw_frame, read+1, 32);
	return Result;
}

EMOKIT_DECLSPEC emokit_device* emokit_create()
{
	emokit_device* s = (emokit_device*)malloc(sizeof(emokit_device));
	s->_is_open = 0;
	s->_is_inited = 1;	
	return s;
}

