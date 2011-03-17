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
	epoc_device* d;
	char data[32];
	if (argc < 2)
	{
		fputs("Missing argument\nExpected: epocd [consumer|research|special]\n", stderr);
		return 1;
	}
  
	if(strcmp(argv[1], "research") == 0)
		type = RESEARCH_HEADSET;
	else if(strcmp(argv[1], "consumer") == 0)
		type = CONSUMER_HEADSET;
	else if(strcmp(argv[1], "special") == 0)
		type = SPECIAL_HEADSET;
	else {
		fputs("Bad headset type argument\nExpected: epocd [consumer|research|special] source [dest]\n", stderr);
		return 1;
	}
  
	epoc_init(type);

	d = epoc_create();
	printf("Current epoc devices connected: %d\n", epoc_get_count(d, EPOC_VID, EPOC_PID));
	if(epoc_open(d, EPOC_VID, EPOC_PID, 0) != 0)
	{
		printf("CANNOT CONNECT\n");
		return 1;
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
