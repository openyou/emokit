/* Copyright (c) 2010, Daeken and Skadge
 * Copyright (c) 2011-2012, OpenYou Organization (http://openyou.org)
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

#ifndef LIBEMOKIT_H_
#define LIBEMOKIT_H_

#define E_EMOKIT_DRIVER_ERROR -1
#define E_EMOKIT_NOT_INITED -2
#define E_EMOKIT_NOT_OPENED -3

#include <stdint.h>
#if !defined(WIN32)
#define EMOKIT_DECLSPEC
#else
#define EMOKIT_DECLSPEC __declspec(dllexport)
#endif

/// Vendor ID for all emotiv devices
const static uint32_t EMOKIT_VID = 0x21a1;
/// Product ID for all emotiv devices
const static uint32_t EMOKIT_PID = 0x0001;

/// Out endpoint for all emotiv devices
const static uint32_t EMOKIT_OUT_ENDPT = 0x02;
/// In endpoint for all emotiv devices
const static uint32_t EMOKIT_IN_ENDPT  = 0x82;

struct emokit_contact_quality {//values > 4000 are good
	short F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5;
};

struct emokit_frame {
	unsigned char counter; //loops from 0 to 128 (129 values)
	int F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5; //raw data values
	struct emokit_contact_quality cq;
	char gyroX, gyroY;
	unsigned char battery; //percentage of full charge, read on counter=128
};


#ifdef __cplusplus
extern "C"
{
#endif
	struct emokit_device;
	/**
	 * Kills crypto context. Not meant for public calling, call
	 * emokit_delete instead.
	 *
	 */
	void emokit_deinit(struct emokit_device* s);

	/**
	 * Create a new struct emokit_device structure and return a pointer to it.
	 * Makes sure structure is initialized properly. To delete, call
	 * emokit_delete().
	 *
	 *
	 * @return new struct emokit_device structure
	 */
	EMOKIT_DECLSPEC struct emokit_device* emokit_create();

	/**
	 * Return the number of devices currently connected to the system
	 *
	 * @param s Inited device structure
	 * @param device_vid VID to look for, usually EMOKIT_VID constant
	 * @param device_pid PID to look for, usually EMOKIT_PID constant
	 *
	 * @return Number of devices currently connected to system, or < 0
	 * for error
	 */
	EMOKIT_DECLSPEC int emokit_get_count(struct emokit_device* s,
																			 int device_vid,
																			 int device_pid);

	/**
	 * Open an inited device
	 *
	 * @param s Inited device structure
	 * @param device_vid VID to look for, usually EMOKIT_VID constant
	 * @param device_pid PID to look for, usually EMOKIT_PID constant
	 * @param device_index Index of device to open on the bus (0 for first device
	 * found)
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_open(struct emokit_device* s,
																	int device_vid,
																	int device_pid,
																	unsigned int device_index);

	/**
	 * Close an opened device
	 *
	 * @param s Currently opened device
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_close(struct emokit_device* s);

	/**
	 * Delete an inited device
	 *
	 * @param dev Initied device strucure
	 */
	EMOKIT_DECLSPEC void emokit_delete(struct emokit_device* dev);

	/**
	 * Read a single raw report from the device. This function will
	 * block until a single report is read. We are guarenteed each
	 * report will be a full message from the device, so we do not need
	 * to maintain read state between reads.
	 *
	 * @param dev Opened device structure
	 *
	 * @return <0 for error, otherwise return the number of bytes read. 
	 */
	EMOKIT_DECLSPEC int emokit_read_data(struct emokit_device* dev);

	/**
	 * Read a single raw report from the device.
	 *
	 * @param dev Opened device structure
	 * @param timeout Max wait time in ms
	 *
	 * @return <0 for error, otherwise return the number of bytes read.
	 */
	EMOKIT_DECLSPEC int emokit_read_data_timeout(struct emokit_device* dev,
																							 unsigned timeout);

	EMOKIT_DECLSPEC struct emokit_frame
	emokit_get_next_frame(struct emokit_device* dev);

	/**
	 * Given a feature report from the device, extract the serial and
	 * create the crypto key. Exposed because why not. Sets "key" field
	 * in device struct.
	 *
	 * @param s Initied, opened device
	 * @param dev_type EMOKIT_CONSUMER or EMOKIT_RESEARCH
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC void emokit_get_crypto_key(struct emokit_device* s,
																						 int dev_type);
	
	/**
	 * Given an emokit_device and an unsigned char array of not
	 * fewer than 32 bytes, load the most recent unencrypted data
	 * frame into the array. Does not return a value.
	*/ 
	EMOKIT_DECLSPEC void emokit_get_raw_frame(struct emokit_device *dev, unsigned char *buf);

#ifdef __cplusplus
};
#endif
#endif //LIBEMOKIT_H_
