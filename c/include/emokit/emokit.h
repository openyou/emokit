/* Copyright (c) 2010, Daeken and Skadge
 * Copyright (c) 2011-2012, Kyle Machulis <kyle@nonpolynomial.com>
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
#include "libusb-1.0/libusb.h"
#else
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#define EMOKIT_DECLSPEC __declspec(dllexport)
#endif

#define EMOKIT_KEYSIZE 16 /* 128 bits == 16 bytes */

//prototypes so we don't need to include mcrypt at this level
struct CRYPT_STREAM;
typedef struct CRYPT_STREAM *MCRYPT;

/// Vendor ID for all emotiv devices
const static uint32_t EMOKIT_VID = 0x21a1;
/// Product ID for all emotiv devices
const static uint32_t EMOKIT_PID = 0x0001;

/// Out endpoint for all emotiv devices
const static uint32_t EMOKIT_OUT_ENDPT = 0x02;
/// In endpoint for all emotiv devices
const static uint32_t EMOKIT_IN_ENDPT  = 0x82;

struct emokit_contact_quality {
	char F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5;
};

struct emokit_frame {
	int F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5;
	struct emokit_contact_quality cq;
	char gyroX, gyroY;
	char battery;
};

typedef struct {
#if !defined(WIN32)
	struct libusb_context* _context;
	struct libusb_device_handle* _device;
	struct libusb_transfer* _in_transfer;
	struct libusb_transfer* _out_transfer;
#else
	HANDLE _dev;
#endif
	unsigned char serial[16]; // USB Dongle serial number
	int _is_open; // Is device currently open
	int _is_inited; // Is device current initialized
	MCRYPT td; // mcrypt context
	unsigned char key[EMOKIT_KEYSIZE]; // crypt key for device
	unsigned char *block_buffer; // temporary storage for decrypt
	int blocksize; // Size of current block
	struct emokit_frame current_frame; // Last information received from headset
	unsigned char raw_frame[32]; // Raw encrypted data received from headset
	unsigned char raw_unenc_frame[32]; // Raw unencrypted data received from headset
} emokit_device;

#ifdef __cplusplus
extern "C"
{
#endif
	/** 
	 * Kills crypto context. Not meant for public calling, call
	 * emokit_delete instead.
	 *
	 */
	void emokit_deinit(emokit_device* s);

	/** 
	 * Create a new emokit_device structure and return a pointer to it.
	 * Makes sure structure is initialized properly. To delete, call
	 * emokit_delete().
	 *
	 *
	 * @return new emokit_device structure
	 */
	EMOKIT_DECLSPEC emokit_device* emokit_create();

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
	EMOKIT_DECLSPEC int emokit_get_count(emokit_device* s, int device_vid, int device_pid);

	/** 
	 * Open an inited device
	 *
	 * @param s Inited device structure
	 * @param device_vid VID to look for, usually EMOKIT_VID constant
	 * @param device_pid PID to look for, usually EMOKIT_PID constant
	 * @param device_index Index of device to open on the bus (0 for first device found)
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_open(emokit_device* s, int device_vid, int device_pid, unsigned int device_index);

	/** 
	 * Close an opened device
	 *
	 * @param s Currently opened device
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_close(emokit_device* s);

	/** 
	 * Delete an inited device
	 *
	 * @param dev Initied device strucure
	 */
	EMOKIT_DECLSPEC void emokit_delete(emokit_device* dev);

	/** 
	 * Read a single raw report from the device. This function will
	 * block until a single report is read. We are guarenteed each
	 * report will be a full message from the device, so we do not need
	 * to maintain read state between reads.
	 *
	 * @param dev Opened device structure
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_read_data(emokit_device* dev);

	/** 
	 * Given a feature report from the device, extract the serial and
	 * create the crypto key. Exposed because why not. Sets "key" field
	 * in device struct.
	 *
	 * @param s Initied, opened device
	 * @param feature_report Feature report obtained from device
	 *
	 * @return 0 if successful, < 0 for error
	 */
	EMOKIT_DECLSPEC int emokit_get_crypto_key(emokit_device* s, const unsigned char* feature_report);
#ifdef __cplusplus
};
#endif
#endif //LIBEMOKIT_H_
