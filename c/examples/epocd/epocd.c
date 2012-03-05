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
  
	epoc_device* d;
  
	d = epoc_create();
	printf("Current epoc devices connected: %d\n", epoc_get_count(d, EPOC_VID, EPOC_PID));
	if(epoc_open(d, EPOC_VID, EPOC_PID, 0) != 0)
	{
		printf("CANNOT CONNECT\n");
		return 1;
	}
	while(1)
	{
		if(epoc_read_data(d) > 0)
		{
			epoc_get_next_frame(d);
			printf("%d %d %d %d %d\n", d->current_frame.gyroX, d->current_frame.gyroY, d->current_frame.F3, d->current_frame.FC6, d->current_frame.P7);
		  
			fflush(stdout);
		}
	}

	epoc_close(d);
	epoc_delete(d);
	return 0;
}
