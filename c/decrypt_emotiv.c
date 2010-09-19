/* Decrypt Emotic EPOC stream using ECB and RIJNDAEL-128 cipher
 * 
 * Usage: decrypt_emotiv (consumer/research) /dev/emotiv/raw > decoded
 * Make sure to pick the right type of device, as this determins the key
 * */

#include <mcrypt.h>
#include <stdio.h>
#include <stdlib.h>

#define KEYSIZE 16 /* 128 bits == 16 bytes */

unsigned char CONSUMERKEY[KEYSIZE] =  {0x31,0x00,0x35,0x54,0x38,0x10,0x37,0x42,0x31,0x00,0x35,0x48,0x38,0x00,0x37,0x50};
unsigned char RESEARCHKEY[KEYSIZE] =  {0x31,0x00,0x39,0x54,0x38,0x10,0x37,0x42,0x31,0x00,0x39,0x48,0x38,0x00,0x37,0x50};

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
    fputs("File read error", stderr);
    return 1;
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
