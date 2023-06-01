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

### perform peaksense
def perform_peaksense(sample, control, quality_threshold, smoothing_factor, chromosomes, maxima_order, harmonic_threshold, width):

    # parse BAMs
    df_sample = f.parse_bam(sample)
    df_control = f.parse_bam(control)

    # quality cleanup
    df_sample, df_control = f.quality_cleanup(df_sample, df_control, quality_threshold=quality_threshold)

    # coverage & smoothing
    smoothed_sample_cov, smoothed_control_cov = \
        f.compute_coverages(df_sample, df_control, smoothing_factor=smoothing_factor, chromosomes=chromosomes)
    
    # find peaks according to smoothed harmonic
    local_maxima, smoothed_harmonic = \
        f.get_local_maxima(smoothed_sample_cov, smoothed_control_cov, chromosomes, maxima_order=maxima_order)
    
    # clean peaks with harmonic threshold
    cleaned_maxima = f.clean_peaks(local_maxima, smoothed_harmonic, harmonic_threshold=harmonic_threshold)

    # generate BED
    f.maxima_to_bed(maxima=cleaned_maxima, smoothed_harmonic=smoothed_harmonic, width=width, sample_bam_fname=sample)
    return

def perform_viz_alignments(file):
    f.parse_bam(file, viz=True)
    return

def perform_viz_peaks(file):
    f.parse_bed(file, viz=True)
    return

# main function
def main():

    # main parser
    parser = argparse.ArgumentParser(description='PeakSense CLI')
    subparsers = parser.add_subparsers(dest='command')

    # subparsers
    peaksense_parser = subparsers.add_parser('peaksense', help='Perform peaksense analysis')
    viz_alignments_parser = subparsers.add_parser('viz_alignments' , help='Visualize alignment sample & control')
    viz_peaks_parser = subparsers.add_parser('viz_peaks', help='Visualize outputted peaks')

    # peaksense
    peaksense_parser.add_argument('sample', help='Sample file. Accepts BAM & SAM. File can be sorted, or unsorted. File will be indexed by PeakSense.', type=str, metavar='FILE')
    peaksense_parser.add_argument('control', help='Control file. Accepts BAM & SAM. File can be sorted, or unsorted. File will be indexed by PeakSense.', type=str, metavar='FILE')
    peaksense_parser.add_argument('-w', "--width-peaks", help='Peak widths to retun. Accepts positive integer value.', type=positive_int, default=75)
    peaksense_parser.add_argument('-c', "--chromosomes", nargs="+", help="Chromosome names to analyze. Use 'all' to analyze all chromosomes. Separate multiple names with spaces.", default='all', type=str)
    peaksense_parser.add_argument('-q', "--quality-threshold", help="Quality threshold for alignment quality control. All aligned reads below this threshold are removed from BAM file. Accepts non-negative integer value.", type=nonnegative_int, default=35)
    peaksense_parser.add_argument('-s', "--smoothing-factor", help="Higher values produce smoother coverage curves & remove outliers. Values too high can reduce data quality. Accepts positive integer value.", type=positive_int, default=3)
    peaksense_parser.add_argument('-m', "--maxima-order", help="Window size in which peaks are analyzed. Higher values identify longer peaks. Accepts positive integer value.", type=positive_int, default=10)
    peaksense_parser.add_argument('-ht', "--harmonic-threshold", help="Harmonic threshold filters out low-confidence peaks. Accepts non-negative integer value.", type=nonnegative_int, default=20)

    # viz_alignments
    viz_alignments_parser.add_argument('file', help='Sample or control file. Accepts BAM & SAM. File can be sorted, or unsorted. File will be indexed by PeakSense.', type=str, metavar='FILE')

    # viz_peaks
    viz_peaks_parser.add_argument('file', help='Output peaks file. Accepts BED. File can be produced by HOMER or PeakSense.', type=str, metavar='FILE')

    # parse all arguments
    args = parser.parse_args()
    command = args.command
    
    # peaksense
    if command=='peaksense':
        # parse args
        sample = args.sample
        control = args.control
        width = args.width_peaks
        chromosomes = args.chromosomes
        quality_threshold = args.quality_threshold
        smoothing_factor = args.smoothing_factor
        maxima_order = args.maxima_order
        harmonic_threshold = args.harmonic_threshold

        # call peaksense
        perform_peaksense(sample, control, quality_threshold, smoothing_factor, chromosomes, maxima_order, harmonic_threshold, width)

    # parse viz_alignments args
    elif command=='viz_alignments':
        file = args.file
        perform_viz_alignments(file)

    # parse viz_peaks args
    elif command=='viz_peaks':
        file = args.file
        perform_viz_peaks(file)

    # return
    return

if __name__ == '__main__':
    main()