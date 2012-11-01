/**
 * This header defines the methods to access the processed emokit input
 *
 */
#include "emokit/emo_dsp.h"
#define max(a,b) (((a) > (b)) ? (a) : (b))
#define min(a,b) (((a) < (b)) ? (a) : (b))

//Initialize a new struct
//emo_dsp_state make_new_dsp_state();

//void fft_channel(emo_dsp_state* s,int i);

//Shifts all the windows back windows the data 
//executes the fft on each window
//Calculates the power statistics per band
//Calculates the correlation matrix per band
//void process_frame(emo_dsp_state* s, struct emokit_frame* current_frame);

//Reads a new unencrypted frame,
//shifts all the windows back windows the data 
//executes the fft on each window
//Calculates the power statistics per band
//Calculates the correlation matrix per band


/*Calculates the fft of the data in window and stores
 * at f_frame
 */
void fft_channel(emo_dsp_state *s,int i)
{
    //Pointer to the channels data
    fftw_complex* channel = s->channels[i];

    //Window the measurements 
    int ix=0;
    for(ix=0;ix<W_SIZE;ix++)
    {
        s->windowed[ix][0] = s->window[ix]*channel[ix][0];
        s->windowed[ix][1] = s->window[ix]*channel[ix][1];
    }
 
 
    //FFT the frame
    fftw_plan         fftplan = fftw_plan_dft_1d(W_SIZE, s->windowed, s->f_channels[i], FFTW_FORWARD, FFTW_ESTIMATE); 
    fftw_execute     (fftplan);
    fftw_destroy_plan(fftplan);

    //Calculate the band powers    
    //Scale the dc offset and highest entry so we can use the same 
    //band measurements
    
    double sqrt_2 = sqrt(2);
    s->f_channels[i][0][0]/=sqrt_2;
    s->f_channels[i][W_SIZE/2-1][0]/=sqrt_2;
   
    int b =0; 
    int b_ix = 0;
    double power_accum;
    for(b=0; b<5 ;b++)
    {   
        power_accum    = 0;
        (s->b_powers[i])[b] = 0;
        //Iterate over all the bands
        //XXX:Check power definition
        for(b_ix = s->band_start_ix[b]; b_ix<=s->band_end_ix[b];b_ix ++)
        {
            power_accum += 2*(s->f_channels[i][b_ix][0]*s->f_channels[i][b_ix][0]+s->f_channels[i][b_ix][1]*s->f_channels[i][b_ix][1]);
        }
        //XXX: is it right to do this or should we leave them squared.
        s->b_powers[i][b]= sqrt(power_accum);
    } 

    //Restore the measurements
    s->f_channels[i][0][0]*=sqrt_2;
    s->f_channels[i][W_SIZE/2-1][0]*=sqrt_2; 
    //Done calculating the band powers 

    //Calculate the total power of the centered data
    s->c_power[i] = 0;
    int j = 0;
    for(j=0;j<W_SIZE;j++)
    {
        s->c_power[i]+=(s->f_channels[i][j][0]*s->f_channels[i][j][0]+s->f_channels[i][j][1]*s->f_channels[i][j][1]);
    }
    s->c_power[i] = sqrt(s->c_power[i]);

}

//Calculates and sets the values of the window
void set_hamming_window(double* window, int length)
{
    int j = 0;
    for(j=0;j<length;j++)
        *(window+j) = 0.54 + 0.46*cos(2*M_PI*((double)j/(length+1)));

}

//Calls process frame but receives a pointer to the device as parameter.
void process_frame_from_device(emo_dsp_state* s, emokit_device* dev)
{
    process_frame(s,&dev->current_frame);
}

//Shifts all the channel buffers back and inserts the new measurements
//Windows each channel and executes the fft
//Calculates the power in each band
//Calculates the power of the centered data
//Calculates the cross correlation between all pairs of channels
void process_frame(emo_dsp_state* s, struct emokit_frame* current_frame)
{
    //Make an array to copy the values into and access sequentially
    int frame_vals[14];

    frame_vals[0]  = current_frame->F3;
	frame_vals[1]  = current_frame->FC6;
	frame_vals[2]  = current_frame->P7;
	frame_vals[3]  = current_frame->T8;
	frame_vals[4]  = current_frame->F7;
	frame_vals[5]  = current_frame->F8;
	frame_vals[6]  = current_frame->T7;
	frame_vals[7]  = current_frame->P8;
	frame_vals[8]  = current_frame->AF4;
	frame_vals[9]  = current_frame->F4;
	frame_vals[10] = current_frame->AF3;
	frame_vals[11] = current_frame->O2;
	frame_vals[12] = current_frame->O1;
	frame_vals[13] = current_frame->FC5;

    //Shift all the arrays back and append the new value converted to fftw_complex
    int f = 0;
    int i = 0;
    for(f=0;f<14;f++)
    {

        //Shift all the frames back
        for(i=1<i;i<W_SIZE;i++)
        {
            (s->channels[f])[i-1][0] = (s->channels[f])[i][0];
            //s->frames[f][i-1][1] = s->frames[f][i][1]; /Were only dealing with real data here
        }
        //Save the new value
        (s->channels[f])[W_SIZE-1][0] = ((double)(frame_vals[f]-EPOC_HLF))/(double)EPOC_HLF;
        //Process the channel 
        fft_channel(s,f);
    }


}

emo_dsp_state* make_new_dsp_state()
{
    emo_dsp_state *p = (emo_dsp_state*)malloc(sizeof(emo_dsp_state));
  
    //Indices where each p.band starts and ends
    p->band_start_ix[0] = 0; 
    p->band_start_ix[1] = 4;
    p->band_start_ix[2] = 8;
    p->band_start_ix[3] = 13;
    p->band_start_ix[4] = 30;
    
    p->band_end_ix[0]   = 3;
    p->band_end_ix[1]   = 7;
    p->band_end_ix[2]   = 12;
    p->band_end_ix[3]   = 29;
    p->band_end_ix[4]   = 64;

    //XXX:
    //Make this a hamming window
    int i = 0;
    for(i = 0; i< W_SIZE;i++)
    {
        p->window[i] = 1.0;
    }

    return p;
}
 
double calculate_cross_corr_band(emo_dsp_state *s,int chan_1, int chan_2, int band)
{
    double accum = 0;
    fftw_complex* c1 = s->f_channels[chan_1];
    fftw_complex* c2 = s->f_channels[chan_2];
    //Find the 4 indices for the band limits
    int ixs_1, ixe_1, ixs_2, ixe_2;
    ixs_1  = s->band_start_ix[band];
    ixe_1  = s->band_end_ix[band]; 
    
    if(ixs_1==0) //band contains the DC offset
    {
        ixs_1 += 1; //shorten the band so that we dont add the dc offset 
    }    
    
    if(ixe_1==W_SIZE/2) //Highest band needs something special to prevent double counting
    {
        ixs_2 = W_SIZE/2+1;
        ixe_2 = W_SIZE-ixs_1;
    } 
    else
    {
       ixs_2 = W_SIZE-ixe_1;
       ixe_2 = W_SIZE-ixs_1;
    }
    int k = ixs_1;
    for(k=k;k<=ixe_1;k++)
    {
        accum += c1[k][0]*c2[k][0] + c1[k][1]*c2[k][1];
    }
    for(k=ixs_2;k<=ixe_2;k++)
    {
        accum += c1[k][0]*c2[k][0] + c1[k][1]*c2[k][1];
    }

    //Normalize by the band power
    accum /= (s->b_powers[chan_1][band]*s->b_powers[chan_2][band]);
}

double get_b_power(emo_dsp_state* s, int chan, int band)
{
    return s->b_powers[chan][band];
}

double get_f_channel(emo_dsp_state* s, int chan, int ix, int cplx)
{
    return s->f_channels[chan][ix][cplx];
}

double get_channel(emo_dsp_state* s, int chan, int ix)
{
    return s->channels[chan][ix][0];
}

double get_cros_corr(emo_dsp_state *s, int chan_1, int chan_2, int band)
{ 
    return calculate_cross_corr_band(s,chan_1,chan_2,band);
}


