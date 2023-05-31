# imports
import pysam
import pybedtools
from tqdm import tqdm
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

# activations
tqdm.pandas()

def parse_bam(bam_file, viz=False):
    # index files
    pysam.index(bam_file)
    
    # open BAM file
    aligned_sample = pysam.AlignmentFile(bam_file)
    length = aligned_sample.count()
    aligned_sample.close()
    aligned_sample = pysam.AlignmentFile(bam_file)

    data = []
    for alignment in tqdm(aligned_sample, total=length):
        chrom = alignment.reference_name
        start = alignment.reference_start
        end = alignment.reference_end
        qual = alignment.mapping_quality
        seq = alignment.query_sequence
        data.append(np.asarray([chrom,start,end,qual,seq]))

    # close pysam files
    aligned_sample.close()
    
    # create DataFrame from collected data
    data = np.asarray(data)
    df = pd.DataFrame({'chrom': data[:,0], 'start': data[:,1], 'end': data[:,2], 'qual': data[:,3],
                       'seq': data[:,4]})
    
    # very basic feature generation and data cleaning
    df['read_length'] = df['seq'].apply(len)
    df = df.dropna(how='any')
    int_cols = ['start','end','qual','read_length']
    for col in int_cols:
        df[col] = df[col].astype('int')
    chroms = df['chrom'].value_counts()[df['chrom'].value_counts() > 1000].index.to_list()
    heights = [(df['chrom']==chrom).sum() for chrom in chroms]

    # all prints
    print('File name:', bam_file.upper())
    print('Number of intervals:', df.shape[0])
    print('Average read length:', round(df['read_length'].mean(), 2))
    print('Average read quality:', round(df['qual'].mean(), 2))

    if viz:
        # visualize df
        fig, ax = plt.subplots(2,2,figsize=(15,9))
        ax[0,0].boxplot(df['read_length'])
        ax[0,0].set(title='Read lengths')
        ax[0,1].hist(df['qual'], density=True)
        ax[0,1].set(title='Read qualities')
        ax[1,0].hist(df['start'])
        ax[1,0].set(title='Starting positions')
        ax[1,1].barh(chroms, heights)
        ax[1,1].set(title='Chromosomes')
        plt.show()
    
    # return parsed DataFrame
    return df


def parse_bed(bed_file, viz=False):
    # populate fields for DataFrame
    benchmark_file = pybedtools.BedTool(bed_file)
    read_lengths = [int(interval.length) for interval in benchmark_file]
    scores = [float(interval.score) for interval in benchmark_file if interval.score is not None]
    num_intervals = benchmark_file.count()
    total_length = sum(interval.length for interval in benchmark_file)
    starts = [interval.start for interval in benchmark_file]
    ends = [interval.end for interval in benchmark_file]
    chroms = [interval.chrom for interval in benchmark_file]

    # create DataFrame
    df = pd.DataFrame({'chrom': chroms, 'start': starts, 'end': ends, 'read_length': read_lengths, 'score': scores})
    
    # minimal data cleaning & feature engineering
    df = df.sort_values(by=['start'])[df['chrom'] == '17'].reset_index(drop=True)
    df['dist'] = df['start'] - df['end'].shift(1)
    df['peak'] = (df['read_length'] / 2 + df['start']).astype('int')

    # all prints
    print('Number of intervals:', num_intervals)
    print('Number of overlapping intervals:', (df['dist'] < 0).sum())
    print('Total length:', total_length)
    print('Average interval length:', total_length/num_intervals)
    
    unique_chroms, value_chroms = pd.Series(chroms).value_counts().index.to_list(), \
                                  pd.Series(chroms).value_counts().values

    if viz:
        # all visualizations
        fig, ax = plt.subplots(2,2,figsize=(15,9))
        ax[0,0].boxplot(read_lengths)
        ax[0,0].set(title='Interval lengths')
        ax[0,1].boxplot(scores)
        ax[0,1].set(title='Scores')
        ax[1,0].hist(starts)
        ax[1,0].set(title='Starting positions')
        ax[1,1].barh(unique_chroms, value_chroms)
        ax[1,1].set(title='Chromosomes')
        plt.show()
    
    # return parsed DataFrame
    return df


# quality clean-up
def quality_cleanup(df_sample, df_control, quality_threshold=30):
    df_sample = df_sample[df_sample['qual'] >= quality_threshold].reset_index(drop=True)
    df_control = df_control[df_control['qual'] >= quality_threshold].reset_index(drop=True)
    print('Cleaned alignments: sample number of reads:', df_sample.shape[0])
    print('Cleaned alignments: control number of rows:', df_control.shape[0])
    return df_sample, df_control

# in order to ensure proper comparison, we must not assume that the BAM files are properly normalized
# sample and control may have different counts of reads, and reads need to be either normalized or removed


def compute_coverages(df_sample, df_control, smoothing_factor=5, chromosomes='all'):
    
    # helper function for individual chromosome coverage
    def chromosome_coverage(df_sample, df_control, chrom):
    
        # helper function update coverage
        def update_coverage(row, cov):
            cov[row['start']:row['end']] += 1

        # initialize arrays
        arr_max = max([df_sample[df_sample['chrom'].astype('str') == str(chrom)]['end'].max(),
                       df_control[df_control['chrom'].astype('str') == str(chrom)]['end'].max()])
        sample_cov, control_cov = np.zeros(arr_max), np.zeros(arr_max)

        # populate sample array
        print(f'Chromosome {chrom}, sample')
        if (df_sample['chrom']==str(chrom)).sum() > 0:
            df_sample[df_sample['chrom'].astype('str')==str(chrom)].progress_apply(
                lambda row: update_coverage(row, sample_cov), axis=1
            )

        # populate control array
        print(f'Chromosome {chrom}, control')
        if (df_control['chrom']==str(chrom)).sum() > 0:
            df_control[df_control['chrom'].astype('str')==str(chrom)].progress_apply(
            lambda row: update_coverage(row, control_cov), axis=1
        )

        # return sample and control coverages
        return sample_cov, control_cov
    
    # validate chromosomes
    if chromosomes=='all':
        chromosomes = df_sample['chrom'].unique()
    else:
        if type(chromosomes) != list:
            raise Exception(f'`chromosomes` argument must be a list')
        for chrom in chromosomes:
            if (df_sample['chrom'].astype('str')==str(chrom)).sum() == 0:
                raise Exception(f'Chromosome {chrom} does not exist in sample')
    
    # iterate over all chromosomes and get coverage
    smoothed_sample_cov, smoothed_control_cov = {}, {}
    for chrom in chromosomes:
        sample_cov, control_cov = chromosome_coverage(df_sample, df_control, chrom)
        print('Smoothing...')
        smoothed_sample_cov[str(chrom)] = \
            np.convolve(sample_cov, np.ones(smoothing_factor)/smoothing_factor, mode='valid')
        smoothed_control_cov[str(chrom)] = \
            np.convolve(control_cov, np.ones(smoothing_factor)/smoothing_factor, mode='valid')
    return smoothed_sample_cov, smoothed_control_cov


def get_local_maxima(smoothed_sample_cov, smoothed_control_cov, chromosomes, maxima_order=10):
    local_maxima, smoothed_harmonic = {}, {}
    for chrom in chromosomes:
        chrom = str(chrom)
        print(f'Predicting peaks at chromosome {chrom}...')
        smoothed_harmonic[chrom] = (smoothed_sample_cov[chrom] - smoothed_control_cov[chrom]) *\
                            (smoothed_sample_cov[chrom] / (smoothed_control_cov[chrom] + 1))
        local_maxima[chrom] = argrelextrema(smoothed_harmonic[chrom], np.greater, order=maxima_order)[0]
        print(f'Local maxima: non-clean number of peaks at chromosome {chrom}: {local_maxima[chrom].shape[0]}')
    return local_maxima, smoothed_harmonic


# clean out peaks with low subtracted count
def clean_peaks(local_maxima, smoothed_harmonic, harmonic_threshold=20):
    cleaned_maxima = {}
    for chrom, peaks in local_maxima.items():
        chrom = str(chrom)
        cleaned_maxima[chrom] = np.array([])
        for peak in peaks:
            if smoothed_harmonic[chrom][peak] >= harmonic_threshold:
                cleaned_maxima[chrom] = np.append(cleaned_maxima[chrom], peak)
        reduction_percentage = (1 - round(cleaned_maxima[chrom].shape[0] / peaks.shape[0], 4)) * 100
        print(f'Cleaned maxima: clean number of peaks at chromosome {chrom}: {cleaned_maxima[chrom].shape[0]} \
              ({reduction_percentage}% reduction)')
    return cleaned_maxima

# convert cleaned peaks to BED
def maxima_to_bed(maxima, smoothed_harmonic, width, sample_bam_fname):
    df = pd.DataFrame(columns=['chr','start','end','score'])
    for chrom, peaks in maxima.items():
        chrom = str(chrom)
        peaks = peaks.astype('int')
        df2 = pd.DataFrame({'chr': chrom, 
                            'start': peaks-int(width/2), 
                            'end': peaks-int(width/2)+1, 
                            'score': smoothed_harmonic[chrom][peaks]})
        df = pd.concat([df, df2], axis=0)
    fname = [term for term in sample_bam_fname.split('.') if term not in ['bam','sam','sorted']]
    fname = '.'.join(fname + ['peaksense', 'bed'])
    df.to_csv(fname, sep='\t', header=False, index=False)
    print(f'File generated: {fname.upper()}')
    return


# visualize random peaks
def visualize_peaks(all_maxima, all_smoothed, chromosome, width=75, maxima_order=10):
    n_peaks = 9
    width = 75
    local_maxima = all_maxima[chromosome]
    smoothed = all_smoothed[chromosome]
    peaks = np.random.choice(local_maxima, n_peaks)
    fig, axes = plt.subplots(3,3,figsize=(15,9))
    axes = axes.flatten()
    for peak, ax in list(zip(peaks, axes)):
        range_x = (int(peak - width/2), int(peak + width/2))
        near_peaks = local_maxima[(local_maxima > range_x[0]) & (local_maxima < range_x[1])]
        ax.plot(range(range_x[0], range_x[1]), smoothed[range_x[0]:range_x[1]])
        [ax.axvline(p, c='red', alpha=0.2, linewidth=maxima_order) for p in near_peaks]
        [ax.axvline(p, c='orange', alpha=0.1, linewidth=width) for p in near_peaks]
    plt.show()


# analyze a range of positions
def find_overlap(df, r, chrom):
    return df[
        ((df['start'].astype('int').between(r[0], r[1])) | 
        (df['end'].astype('int').between(r[0], r[1])) |
        ((df['start'].astype('int') > r[0]) & (df['end'].astype('int') < r[1]))) &
        (df['chrom'].astype('str')==str(chrom))
    ]

