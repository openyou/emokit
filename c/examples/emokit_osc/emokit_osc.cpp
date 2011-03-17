/* 
    Simple example of sending an OSC message using oscpack.
*/

#include <stdio.h>
#include <string.h>
#include "oscpack/osc/OscOutboundPacketStream.h"
#include "oscpack/ip/UdpSocket.h"
#include "libepoc.h"

#define ADDRESS "127.0.0.1"
#define PORT 7000

#define OUTPUT_BUFFER_SIZE 1024

int main(int argc, char* argv[])
{
    UdpTransmitSocket transmitSocket( IpEndpointName( ADDRESS, PORT ) );
    
    char buffer[OUTPUT_BUFFER_SIZE];
    osc::OutboundPacketStream p( buffer, OUTPUT_BUFFER_SIZE );

	FILE *input;
	FILE *output;
	enum headset_type type;
  
	char raw_frame[32];
	struct epoc_frame frame;
	epoc_device* d;
	uint8_t data[32];
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
			p << osc::BeginBundleImmediate
			  << osc::BeginMessage( "/test1" ) 
			  << true << 23 << (float)3.1415 << "hello" << osc::EndMessage
			  << osc::BeginMessage( "/test2" ) 
			  << true << 24 << (float)10.8 << "world" << osc::EndMessage
			  << osc::EndBundle;
    
			transmitSocket.Send( p.Data(), p.Size() );

			//printf("%d %d %d %d %d\n", frame.gyroX, frame.gyroY, frame.F3, frame.FC6, frame.P7);
		  
			fflush(stdout);
		}
	}

	epoc_close(d);
	epoc_delete(d);
	return 0;

}

