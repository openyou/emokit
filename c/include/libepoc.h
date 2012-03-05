/* Copyright (c) 2010, Daeken and Skadge
 * Copyright (c) 2011, Kyle Machulis <kyle@nonpolynomial.com>
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

#ifndef LIBEPOC_H_
#define LIBEPOC_H_

#define E_NPUTIL_DRIVER_ERROR -1
#define E_NPUTIL_NOT_INITED -2
#define E_NPUTIL_NOT_OPENED -3

#include <stdint.h>
#if !defined(WIN32)
#define EPOC_DECLSPEC
#include "libusb-1.0/libusb.h"
#else
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#define EPOC_DECLSPEC __declspec(dllexport)
#endif

#define EPOC_KEYSIZE 16 /* 128 bits == 16 bytes */

//prototypes so we don't need to include mcrypt at this level
struct CRYPT_STREAM;
typedef struct CRYPT_STREAM *MCRYPT;

/// Vendor ID for all emotiv devices
const static uint32_t EPOC_VID = 0x21a1;
/// Product ID for all emotiv devices
const static uint32_t EPOC_PID = 0x0001;

/// Out endpoint for all emotiv devices
const static uint32_t EPOC_OUT_ENDPT = 0x02;
/// In endpoint for all emotiv devices
const static uint32_t EPOC_IN_ENDPT  = 0x82;

struct epoc_contact_quality {
char F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5;
};

struct epoc_frame {
int F3, FC6, P7, T8, F7, F8, T7, P8, AF4, F4, AF3, O2, O1, FC5;
struct epoc_contact_quality cq;
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
unsigned char serial[16];
int _is_open;
int _is_inited;
MCRYPT td;
unsigned char key[EPOC_KEYSIZE];
unsigned char *block_buffer;
int blocksize;
struct epoc_frame current_frame;
unsigned char raw_frame[32];
unsigned char raw_unenc_frame[32];
} epoc_device;

#ifdef __cplusplus
extern "C"
{
#endif
EPOC_DECLSPEC int epoc_init();
EPOC_DECLSPEC int epoc_deinit();

EPOC_DECLSPEC int epoc_get_next_raw(epoc_device* s);
EPOC_DECLSPEC int epoc_get_next_frame(epoc_device* s);

EPOC_DECLSPEC epoc_device* epoc_create();
EPOC_DECLSPEC int epoc_get_count(epoc_device* s, int device_vid, int device_pid);
EPOC_DECLSPEC int epoc_open(epoc_device* s, int device_vid, int device_pid, unsigned int device_index);
EPOC_DECLSPEC int epoc_close(epoc_device* s);
EPOC_DECLSPEC void epoc_delete(epoc_device* dev);
EPOC_DECLSPEC int epoc_read_data(epoc_device* dev);
EPOC_DECLSPEC int epoc_get_crypto_key(epoc_device* s, const unsigned char* feature_report);
#ifdef __cplusplus
};
#endif
#endif //LIBEPOC_H_
