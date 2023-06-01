⚠️ WARNING: ⚠️

Running PeakSense may take up substantial memory. If running at 16GB RAM or less, limit your calls to only the most important chromosomes for every run (for example, the example dataset has alignments for all chromosomes, yet is truly chr17). Using DataHub or another machine with access to 48GB+ RAM will give you more flexibility.

# PeakSense: Deep Learning-based Peak Calling Tool

PeakSense is a command-line tool written in Python that utilizes deep learning techniques to recreate HOMER's findPeaks function. It is designed to convert files in various formats (such as BAM, SAM, sorted, or unsorted) into a BED file containing peak intervals. PeakSense is specifically tailored for transcription factors and provides users with control over several options to customize the peak calling process.

## Features
* Converts BAM, SAM, sorted, or unsorted files into a BED file with peak intervals
* Specifically optimized for transcription factors
* Allows customization of the following options:
  * Peak width: Users can specify the desired peak widths (positive integer values)
  * Chromosomes: Users can choose specific chromosome names for analysis or select 'all' for analyzing all chromosomes
  * Alignment quality threshold: Sets a quality threshold for alignment quality control, removing reads below this threshold (non-negative integer values)
  * Smoothing factor: Adjusts the smoothness of coverage curves and removes outliers (positive integer values)
  * Maxima order: Defines the window size for analyzing peaks, with higher values identifying longer peaks (positive integer values)
  * Harmonic threshold: Filters out low-confidence peaks (non-negative integer values)

## Installation
Please note that installation requires Python 3.x.

1. Clone the repository:
```
git clone https://github.com/ericcherny/PeakSense.git
```
2. Install the package using setup.py:
```
cd PeakSense
python3 setup.py install
```

## Usage
To use PeakSense, run the following command:
```
peaksense [options] <input_file1> <input_file2>
```
Replace <input_file1>, <input_file2>, etc. with the paths to your input sample and control files, respectively. 

To see all available options and their descriptions, use the --help or -h flag:
```
peaksense --help
```
## Command Line Arguments

The following are the command line arguments for PeakSense:

- `bam_sample` (required): Sample file. Accepts BAM & SAM formats. The file can be sorted or unsorted. The file will be indexed by PeakSense.

- `bam_control` (required): Control file. Accepts BAM & SAM formats. The file can be sorted or unsorted. The file will be indexed by PeakSense.

- `-w` or `--width-peaks` (optional): Peak widths to return for transcription peak intervals. Accepts a positive integer value. Default: 75.

- `-c` or `--chromosomes` (optional): Chromosome names to analyze. Use 'all' to analyze all chromosomes. Separate multiple names with spaces. Default: 'all'.

- `-q` or `--quality-threshold` (optional): Quality threshold for alignment quality control. All aligned reads below this threshold will be removed from the BAM file. Accepts a non-negative integer value. Default: 35.

- `-s` or `--smoothing-factor` (optional): Smoothing factor for coverage curves. Higher values produce smoother curves and minimize spikes. However, values that are too high can reduce data quality. Accepts a positive integer value. Default: 3.

- `-m` or `--maxima-order` (optional): Window size in which peaks are analyzed. Higher values identify longer peaks. Accepts a positive integer value. Default value is 10.
   - ⚠️ Note: higher values are memory and time intensive ⚠️

- `-ht` or `--harmonic-threshold` (optional): Harmonic threshold for filtering out low-confidence peaks. Accepts a non-negative integer value. Default value is 20.


## Examples
Here are some example usages of PeakSense:
```
peaksense examples/Klf4.sorted.bam examples/control.sorted.bam -c 17
```
This command will call peaks using the specified sample and control input files (Klf4.sorted.bam and control.sorted.bam) and limit the analysis to chromosome 17.

## Issues and Contributions
If you encounter any issues while using PeakSense or have suggestions for improvements, please create an issue on the GitHub repository. Contributions are also welcome through pull requests.

## License
PeakSense is licensed under the MIT License. See LICENSE for more information.

## Acknowledgments
We would like to thank the developers of HOMER for their valuable work, which inspired PeakSense.

## Contact
For any further questions or inquiries, please contact eric@internalize.io.
