# imports
import argparse
from peaksense import functions as f

# validation functions
def nonnegative_int(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("Value must be a non-negative integer.")
    return ivalue

def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer")
    return ivalue

# main function
def main():
    parser = argparse.ArgumentParser(
        prog='peaksense',
        description='Perform peak finding on transcription factors'
    )

    # arguments
    parser.add_argument('bam_sample', help='Sample file. Accepts BAM & SAM. File can be sorted, or unsorted. File will be indexed by PeakSense.', type=str)
    parser.add_argument('bam_control', help='Control file. Accepts BAM & SAM. File can be sorted, or unsorted. File will be indexed by PeakSense.', type=str)
    parser.add_argument('-w', "--width-peaks", help='Peak widths to retun. Accepts positive integer value.', type=positive_int, default=75)
    parser.add_argument('-c', "--chromosomes", nargs="+", help="Chromosome names to analyze. Use 'all' to analyze all chromosomes. Separate multiple names with spaces.", default='all', type=str)
    parser.add_argument('-q', "--quality-threshold", help="Quality threshold for alignment quality control. All aligned reads below this threshold are removed from BAM file. Accepts non-negative integer value.", type=nonnegative_int, default=35)
    parser.add_argument('-s', "--smoothing-factor", help="Higher values produce smoother coverage curves & remove outliers. Values too high can reduce data quality. Accepts positive integer value.", type=positive_int, default=3)
    parser.add_argument('-m', "--maxima-order", help="Window size in which peaks are analyzed. Higher values identify longer peaks. Accepts positive integer value.", type=positive_int, default=10)
    parser.add_argument('-ht', "--harmonic-threshold", help="Harmonic threshold filters out low-confidence peaks. Accepts non-negative integer value.", type=nonnegative_int, default=20)

    # parse arguments
    args = parser.parse_args()
    bam_sample = args.bam_sample
    bam_control = args.bam_control
    width = args.width_peaks
    chromosomes = args.chromosomes
    quality_threshold = args.quality_threshold
    smoothing_factor = args.smoothing_factor
    maxima_order = args.maxima_order
    harmonic_threshold = args.harmonic_threshold

    ### perform
    # parse BAMs
    df_sample = f.parse_bam(bam_sample)
    df_control = f.parse_bam(bam_control)

    # quality cleanup
    df_sample, df_control = f.quality_cleanup(df_sample, df_control, quality_threshold=35)

    # coverage & smoothing
    smoothed_sample_cov, smoothed_control_cov = \
        f.compute_coverages(df_sample, df_control, smoothing_factor=smoothing_factor, chromosomes=chromosomes)
    
    # find peaks according to smoothed harmonic
    local_maxima, smoothed_harmonic = \
        f.get_local_maxima(smoothed_sample_cov, smoothed_control_cov, chromosomes, maxima_order=10)
    
    # clean peaks with harmonic threshold
    cleaned_maxima = f.clean_peaks(local_maxima, smoothed_harmonic, harmonic_threshold=harmonic_threshold)

    # generate BED
    f.maxima_to_bed(maxima=cleaned_maxima, smoothed_harmonic=smoothed_harmonic, width=width, sample_bam_fname=bam_sample)

    # return
    return

if __name__ == '__main__':
    main()