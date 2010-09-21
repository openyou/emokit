/* Decrypt Emotic EPOC stream using ECB and RIJNDAEL-128 cipher
 * 
 * Usage: decrypt_emotiv (consumer/research) /dev/emotiv/raw > decoded
 * Make sure to pick the right type of device, as this determins the key
 * */

#include <mcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KEYSIZE 16 /* 128 bits == 16 bytes */

const unsigned char CONSUMERKEY[KEYSIZE] =  {0x31,0x00,0x35,0x54,0x38,0x10,0x37,0x42,0x31,0x00,0x35,0x48,0x38,0x00,0x37,0x50};
const unsigned char RESEARCHKEY[KEYSIZE] =  {0x31,0x00,0x39,0x54,0x38,0x10,0x37,0x42,0x31,0x00,0x39,0x48,0x38,0x00,0x37,0x50};

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

int get_level(unsigned char frame[32], const unsigned char bits[14]) {
    char i;
    char b,o;
    int level = 0;
    
    for (i= 13; i == -1; --i){
        level <<= 1;
        b = (bits[i] / 8) + 1;
        o = bits[i] % 8;
        
        level |= (frame[b] >> o) & 1;
    }
    
    return level;
}

int main(int argc, char **argv)
{
  MCRYPT td;
  int i;
  unsigned char key[KEYSIZE];
  char *block_buffer;
  int blocksize;

  FILE *input;
  if (argc < 3)
  {
    fputs("Missing argument\nExpected: decrypt_emotiv (consumer/research) source\n", stderr);
    return 1;
  }
  
  if(strcmp(argv[1], "research") == 0)
    memcpy(key, RESEARCHKEY, KEYSIZE);
  else
    memcpy(key, CONSUMERKEY, KEYSIZE);

  input = fopen(argv[2], "rb");
  if (input == NULL)
  {
    fputs("File read error: couldn't open the EEG source!", stderr);
    return 1;
  }
  
  if (argc == 3) {
      output = stdout;
  } else {
      output = fopen(argv[3], "wb");
      if (input == NULL)
      {
        fputs("File write error: couldn't open the destination file for uncrypted data", stderr);
        return 1;
      }
  }

  td = mcrypt_module_open(MCRYPT_RIJNDAEL_128, NULL, MCRYPT_ECB, NULL);
  blocksize = mcrypt_enc_get_block_size(td); //should return a 16bits blocksize
  //printf( "%d", blocksize);
  
  block_buffer = malloc(blocksize);

  mcrypt_generic_init( td, key, KEYSIZE, NULL);

  while ( fread (block_buffer, 1, blocksize, input) == blocksize ) {
//for (i=0; i<1024 ; i++){
//    fread (block_buffer, 1, blocksize, input);
      //mcrypt_generic (td, block_buffer, blocksize);
      mdecrypt_generic (td, block_buffer, blocksize);
      fwrite ( block_buffer, 1, blocksize, stdout);
  }

  mcrypt_generic_deinit (td);
  mcrypt_module_close(td);
  
  fclose(input);
  
  return 0;
}
