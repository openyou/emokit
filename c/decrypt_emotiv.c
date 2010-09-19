/* Decrypt Emotic EPOC stream using ECB and RIJNDAEL-128 cipher
 * 
 * Usage: decrypt_emotiv /dev/emotiv/raw > decoded
 * */

#include <mcrypt.h>
#include <stdio.h>
#include <stdlib.h>

#define KEYSIZE 16 /* 128 bits == 16 bytes */

#define CONSUMERKEY {31,0,35,54,38,10,37,42,31,0,35,48,38,0,37,50}
#define RESEARCHKEY {31,0,39,54,38,10,37,42,31,0,39,48,38,0,37,50}

int main(int argc, char **argv)
{
  MCRYPT td;
  int i;
  unsigned char key[KEYSIZE] = RESEARCHKEY;
  char *block_buffer;
  int blocksize;

  FILE *input;
  if (argc < 2)
  {
    fputs("Missing argument\nExpected: decrypt_emotiv source\n", stderr);
    return 1;
  }

  input = fopen(argv[1], "rb");
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
