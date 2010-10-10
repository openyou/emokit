/* Emotic EPOC daemon that decrypt stream using ECB and RIJNDAEL-128 cipher
 * (well, not yet a daemon...)
 * 
 * Usage: epocd (consumer/research) /dev/emotiv/encrypted output_file
 * 
 * Make sure to pick the right type of device, as this determins the key
 * */

#include <stdio.h>
#include <string.h>

#include "libepoc.h"
   

int main(int argc, char **argv)
{
  FILE *input;
  FILE *output;
  enum headset_type type;
  
  char raw_frame[32];
  struct epoc_frame frame;

  /*
  if (argc < 3)
  {
    fputs("Missing argument\nExpected: decrypt_emotiv [consumer|research] source [dest]\n", stderr);
    fputs("By default, dest = stdout\n", stderr);
    return 1;
  }
  
  if(strcmp(argv[1], "research") == 0)
    type = RESEARCH_HEADSET;
  else
    type = CONSUMER_HEADSET;

  input = fopen(argv[2], "rb");
  if (input == NULL)
  {
    fputs("File read error: couldn't open the EEG source!", stderr);
    return 1;
  }
  
  epoc_init(input, type);
  
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

  while ( 1 ) {
      epoc_get_next_frame(&frame);
      printf("F3: %d\n", frame.F3);
      fflush(stdout);
  }

  epoc_close();
  */

  epoc_init(SPECIAL_HEADSET);
  epoc_device* d;
  char data[32];
  d = epoc_create();
  printf("Current epoc devices connected: %d\n", epoc_get_count(d, EPOC_VID, EPOC_PID));
  if(epoc_open(d, EPOC_VID, EPOC_PID, 0) != 0)
  {
	  printf("CANNOT CONNECT\n");
  }
  while(1)
  {
	  if(epoc_read_data(d, data) > 0)
	  {
		  epoc_get_next_frame(&frame, data);
		  printf("%d %d %d %d %d\n", frame.gyroX, frame.gyroY, frame.F3, frame.FC6, frame.P7);
		  
		  fflush(stdout);
	  }
  }

  epoc_close(d);

  epoc_delete(d);
  return 0;
}
