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

#include "emokit/emokit.h"
#include <hidapi.h>
#include <mcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const unsigned char F3_MASK[14] = {10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7}; 
const unsigned char FC6_MASK[14] = {214, 215, 200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195};
const unsigned char P7_MASK[14] = {84, 85, 86, 87, 72, 73, 74, 75, 76, 77, 78, 79, 64, 65};
const unsigned char T8_MASK[14] = {160, 161, 162, 163, 164, 165, 166, 167, 152, 153, 154, 155, 156, 157};
const unsigned char F7_MASK[14] = {48, 49, 50, 51, 52, 53, 54, 55, 40, 41, 42, 43, 44, 45};
const unsigned char F8_MASK[14] = {178, 179, 180, 181, 182, 183, 168, 169, 170, 171, 172, 173, 174, 175};
const unsigned char T7_MASK[14] = {66, 67, 68, 69, 70, 71, 56, 57, 58, 59, 60, 61, 62, 63};
const unsigned char P8_MASK[14] = {158, 159, 144, 145, 146, 147, 148, 149, 150, 151, 136, 137, 138, 139};
const unsigned char AF4_MASK[14] = {196, 197, 198, 199, 184, 185, 186, 187, 188, 189, 190, 191, 176, 177};
const unsigned char F4_MASK[14] = {216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213};
const unsigned char AF3_MASK[14] = {46, 47, 32, 33, 34, 35, 36, 37, 38, 39, 24, 25, 26, 27};
const unsigned char O2_MASK[14] = {140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135, 120, 121};
const unsigned char O1_MASK[14] = {102, 103, 88, 89, 90, 91, 92, 93, 94, 95, 80, 81, 82, 83};
const unsigned char FC5_MASK[14] = {28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9};

struct emokit_device {
	hid_device* _dev;
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
};

struct emokit_device* emokit_create()
{
	struct emokit_device* s = (struct emokit_device*)malloc(sizeof(struct emokit_device));
	s->_is_open = 0;
	s->_is_inited = 0;
	hid_init();
	s->_is_inited = 1;	
	return s;
}

int emokit_get_count(struct emokit_device* s, int device_vid, int device_pid)
{
	int count = 0;
	struct hid_device_info* devices;
	struct hid_device_info* device_cur;
	if (!s->_is_inited)
	{
		return E_EMOKIT_NOT_INITED;
	}
	devices = hid_enumerate(device_vid, device_pid);

	device_cur = devices;
	while(device_cur) {
		++count;
		device_cur = device_cur->next;
	}
	
	hid_free_enumeration(devices);	
	return count;
}

int emokit_open(struct emokit_device* s, int device_vid, int device_pid, unsigned int device_index)
{
	int count = 0;
	struct hid_device_info* devices;
	struct hid_device_info* device_cur;
	if (!s->_is_inited)
	{
		return E_EMOKIT_NOT_INITED;
	}
	devices = hid_enumerate(device_vid, device_pid);

	device_cur = devices;
	while(device_cur) {
		if(count == device_index) {
			s->_dev = hid_open_path(device_cur->path);
			break;
		}
		++count;
		device_cur = device_cur->next;
	}
	
	hid_free_enumeration(devices);
	if(!s->_dev) {
		return E_EMOKIT_NOT_OPENED;
	}
	s->_is_open = 1;
	emokit_init_crypto(s);
	return 0;
}

int emokit_close(struct emokit_device* s)
{
	if(!s->_is_open)
	{
		return E_EMOKIT_NOT_OPENED;
	}
	hid_close(s->_dev);
	s->_is_open = 0;
	return 0;
}

int emokit_read_data(struct emokit_device* s)
{
	return hid_read(s->_dev, s->raw_frame, 32);
}

EMOKIT_DECLSPEC int emokit_get_crypto_key(struct emokit_device* s, const unsigned char* feature_report) {
	unsigned char type = 0x0; //feature[5];
	int i;
	type &= 0xF;
	type = (type == 0);

	unsigned int l = 16;
	
	s->key[0] = s->serial[l-1];
	s->key[1] = '\0';
	s->key[2] = s->serial[l-2];
	if(type) {
		s->key[3] = 'H';
		s->key[4] = s->serial[l-1];
		s->key[5] = '\0';
		s->key[6] = s->serial[l-2];
		s->key[7] = 'T';
		s->key[8] = s->serial[l-3];
		s->key[9] = '\x10';
		s->key[10] = s->serial[l-4];
		s->key[11] = 'B';
	}
	else {
		s->key[3] = 'T';
		s->key[4] = s->serial[l-3];
		s->key[5] = '\x10';
		s->key[6] = s->serial[l-4];
		s->key[7] = 'B';
		s->key[8] = s->serial[l-1];
		s->key[9] = '\0';
		s->key[10] = s->serial[l-2];
		s->key[11] = 'H';
	}
	s->key[12] = s->serial[l-3];
	s->key[13] = '\0';
	s->key[14] = s->serial[l-4];
	s->key[15] = 'P';

	printf("Serial: ");
	for(i = 0; i < 16; ++i) {
		printf("%c", s->serial[i]);
	}
	printf("\nKey: ");
	for(i = 0; i < 16; ++i) {
		printf("%i (%c) ", s->key[i], s->key[i]);
	}
	printf("\n");
}

EMOKIT_DECLSPEC int emokit_init_crypto(struct emokit_device* s) {
	printf("Initializing crypto!\n");
	emokit_get_crypto_key(s, "");

	//libmcrypt initialization
	s->td = mcrypt_module_open(MCRYPT_RIJNDAEL_128, NULL, MCRYPT_ECB, NULL);
	s->blocksize = mcrypt_enc_get_block_size(s->td); //should return a 16bits blocksize
    
	s->block_buffer = malloc(s->blocksize);

	mcrypt_generic_init( s->td, s->key, EMOKIT_KEYSIZE, NULL);
	return 0;
}

void emokit_deinit(struct emokit_device* s) {
	mcrypt_generic_deinit (s->td);
	mcrypt_module_close(s->td);
}

int get_level(unsigned char frame[32], const unsigned char bits[14]) {
	signed char i;
	char b,o;
	int level = 0;
    
	for (i = 13; i >= 0; --i) {
		level <<= 1;
		b = (bits[i] / 8) + 1;
		o = bits[i] % 8;
        
		level |= (frame[b] >> o) & 1;
	}
	return level;
}

EMOKIT_DECLSPEC int emokit_get_next_raw(struct emokit_device* s) {
	//Two blocks of 16 bytes must be read.
	int i;

	if (memcpy (s->block_buffer, s->raw_frame, s->blocksize)) {
		mdecrypt_generic (s->td, s->block_buffer, s->blocksize);
		memcpy(s->raw_unenc_frame, s->block_buffer, 16);
	}
	else {
		return -1;
	}
    
	if (memcpy(s->block_buffer, s->raw_frame + s->blocksize, s->blocksize)) {
		mdecrypt_generic (s->td, s->block_buffer, s->blocksize);
		memcpy(s->raw_unenc_frame + 16, s->block_buffer, 16);
	}
	else {
		return -1;
	}
	return 0;
}

EMOKIT_DECLSPEC struct emokit_frame emokit_get_next_frame(struct emokit_device* s) {

	memset(s->raw_unenc_frame, 0, 32);
	struct emokit_frame k;
	emokit_get_next_raw(s);

	k.counter = s->raw_unenc_frame[0];
	k.F3 = get_level(s->raw_unenc_frame, F3_MASK);
	k.FC6 = get_level(s->raw_unenc_frame, FC6_MASK);
	k.P7 = get_level(s->raw_unenc_frame, P7_MASK);
	k.T8 = get_level(s->raw_unenc_frame, T8_MASK);
	k.F7 = get_level(s->raw_unenc_frame, F7_MASK);
	k.F8 = get_level(s->raw_unenc_frame, F8_MASK);
	k.T7 = get_level(s->raw_unenc_frame, T7_MASK);
	k.P8 = get_level(s->raw_unenc_frame, P8_MASK);
	k.AF4 = get_level(s->raw_unenc_frame, AF4_MASK);
	k.F4 = get_level(s->raw_unenc_frame, F4_MASK);
	k.AF3 = get_level(s->raw_unenc_frame, AF3_MASK);
	k.O2 = get_level(s->raw_unenc_frame, O2_MASK);
	k.O1 = get_level(s->raw_unenc_frame, O1_MASK);
	k.FC5 = get_level(s->raw_unenc_frame, FC5_MASK);
    
	k.gyroX = s->raw_unenc_frame[29] - 102;
	k.gyroY = s->raw_unenc_frame[30] - 104;
    
	k.battery = 0;
	return k;
}

EMOKIT_DECLSPEC void emokit_delete(struct emokit_device* dev)
{
	emokit_deinit(dev);
	free(dev);
}
