/* 
    Simple example of sending an OSC message using oscpack.
*/

#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <csignal>
#include <iostream>
#include "oscpack/osc/OscOutboundPacketStream.h"
#include "oscpack/ip/UdpSocket.h"
#include "libepoc.h"

#define ADDRESS "127.0.0.1"
#define PORT 9997

#define OUTPUT_BUFFER_SIZE 4096

void sigproc(int i)
{
	std::cout << "closing epoc and quitting" << std::endl;
	exit(0);
}

int main(int argc, char* argv[])
{
	signal(SIGINT, sigproc);
#ifndef WIN32
	signal(SIGQUIT, sigproc);
#endif

    UdpTransmitSocket transmitSocket( IpEndpointName( ADDRESS, PORT ) );
    
    char buffer[OUTPUT_BUFFER_SIZE];


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
			osc::OutboundPacketStream p( buffer, OUTPUT_BUFFER_SIZE );
			p << osc::BeginBundleImmediate
			  << osc::BeginMessage( "/epoc/channels" )
			  << frame.F3 << frame.FC6 << frame.P7 << frame.T8 << frame.F7 << frame.F8 << frame.T7 << frame.P8 << frame.AF4 << frame.F4 << frame.AF3 << frame.O2 << frame.O1 << frame.FC5 << osc::EndMessage
			  << osc::BeginMessage( "/epoc/gyro" ) 
			  << frame.gyroX << frame.gyroY << osc::EndMessage
			  << osc::EndBundle;
    
			transmitSocket.Send( p.Data(), p.Size() );
		}
	}

	epoc_close(d);
	epoc_delete(d);
	return 0;

}

