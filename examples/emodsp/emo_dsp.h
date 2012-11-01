/**
 * This header defines the methods to access the processed emokit input
 *
 */
#include "emokit/emokit.h"
#include <fftw3.h> 
#include <math.h>
#include <stdlib.h>

#define W_SIZE 128
#define EPOC_HLF 8192
#define DE 0
#define TH 1
#define AL 2
#define BE 3
#define GA 4

typedef struct
{   
    //Channel history
    fftw_complex channels[14][W_SIZE];
    //Channel fourier transform 
    fftw_complex f_channels[14][W_SIZE];

    //Channel powers
    double c_power[14];
    //band powers
    double  b_powers[14][5];
   
    //Array to save the input to fftw
    fftw_complex windowed[W_SIZE];   
    //Window function coefficients 
    double       window[W_SIZE];

    //Band limits
    int band_start_ix[5]; 
    int band_end_ix[5]; 
    
} emo_dsp_state;

double get_b_power(emo_dsp_state*,int, int);
double get_f_channel(emo_dsp_state*,int,int,int);
double get_channel(emo_dsp_state*,int,int);
void fft_channel(emo_dsp_state*,int);
void process_frame(emo_dsp_state*, struct emokit_frame*);
void process_frame_from_device(emo_dsp_state*, emokit_device*);
emo_dsp_state* make_new_dsp_state();
double get_cros_corr(emo_dsp_state*, int, int, int);
void   set_hamming_window(double *,int);
