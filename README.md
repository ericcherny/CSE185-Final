⚠️ WARNING: ⚠️

Running PeakSense may take up substantial memory. If running at 16GB RAM or less, limit your calls to only the most important chromosomes for every run (for example, the example dataset has alignments for all chromosomes, yet is truly chr17). Using DataHub or another machine with access to 48GB+ RAM will give you more flexibility.

# PeakSense: Deep Learning-based Peak Calling Tool

PeakSense is a command-line tool written in Python that utilizes deep learning techniques to recreate HOMER's findPeaks function. It is designed to convert files in various formats (such as BAM, SAM, sorted, or unsorted) into a BED file containing peak intervals. PeakSense is specifically tailored for transcription factors and provides users with control over several options to customize the peak calling process.

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

## Functions
PeakSense currently supports 3 functions: `peaksense`, `viz_alignments`, `viz_peaks`.

### *peaksense*
The `peaksense` function performs PeakSense analysis on sample and control alignment files. It outputs a BED file containing peak intervals and their respective confidence scores.

#### Arguments
- `sample` (required): Sample file. Accepts BAM & SAM. File can be sorted or unsorted. File will be indexed by PeakSense.
- `control` (required): Control file. Accepts BAM & SAM. File can be sorted or unsorted. File will be indexed by PeakSense.
- `-w, --width-peaks` (optional): Peak widths to return. Accepts positive integer value. Default is 75.
- `-c, --chromosomes` (optional): Chromosome names to analyze. Use 'all' to analyze all chromosomes. Separate multiple names with spaces. Default is 'all'.
- `-q, --quality-threshold` (optional): Quality threshold for alignment quality control. All aligned reads below this threshold are removed from the BAM file. Accepts non-negative integer value. Default is 35.
- `-s, --smoothing-factor` (optional): Smoothing factor for coverage curves. Higher values produce smoother curves and remove outliers. Values too high can reduce data quality. Accepts positive integer value. Default is 3.
- `-m, --maxima-order` (optional): Window size in which peaks are analyzed. Higher values identify longer peaks. Accepts positive integer value. Default is 10.
   - ⚠️ Note: higher values are memory and time intensive ⚠️
- `-ht, --harmonic-threshold` (optional): Harmonic threshold filters out low-confidence peaks. Accepts non-negative integer value. Default is 20.

#### Usage
To use `peaksense`, run the following command:
```
peaksense peaksense <sample_file> <control_file> [options]
```
Replace <sample_file>, <control_file> with the paths to your input sample and control files, respectively. 

To see all available options and their descriptions, use the --help or -h flag:
```
peaksense peaksense --help
```

#### Examples
```
peaksense peaksense examples/Klf4.sorted.bam examples/control.sorted.bam -c 17 8
```
The above function calls `peaksense` on the KLF4 transcription factor, which is primarily aligned on chromosome 17. We included chromosome 17 and chromosome 8 to demonstrate the variation in identified peaks between the true target chromosome and a non-target chromosome.

```
peaksense peaksense examples/Oct4.sorted.bam examples/control.sorted.bam -c 17 1 -q 25 -s 5 -m 5 -ht 40
```
The above function similarly calls `peaksense` on the OCT4 transcription factor. We reduced alignment quality threshold to 25 (giving us more aligned reads to work with), increased smoothing factor (reducing outliers and spikes), reduced maxima order (looking for more local trends), and increased harmonic threshold to 40 (to record more confident peaks).

```
peaksense peaksense examples/Sox2.sorted.bam examples/control.sorted.bam -c all -s 6 -m 4 -ht 40
```
If you have a machine with 48GB+ RAM and have 15+ minutes, you can try running the function on all chromosomes.



### *viz_alignments*

The `viz_alignments` function visualizes the alignments in a BAM or SAM file.

#### Arguments

- `file` (required): Sample or control file. Accepts BAM & SAM. File can be sorted or unsorted. File will be indexed by PeakSense.

#### Usage
To use `viz_alignments`, run the following command:
```
peaksense viz_alignments <file>
```

#### Examples
```
peaksense viz_alignments examples/Klf4.sorted.bam
```
The above calls `viz_alignments` on KLF4 transcription factor.

```
peaksense viz_alignments examples/control.sorted.bam
```
The above calls `viz_alignments` on the control.


### *viz_peaks*

The `viz_peaks` function visualizes the peaks from a BED file.

#### Arguments

- `file` (required): Output peaks file. Accepts BED. File can be produced by HOMER or PeakSense.

#### Usage
To use `viz_peaks`, run the following command:
```
peaksense viz_peaks <file>
```

#### Examples
```
peaksense viz_peaks examples/Klf4.peaks.bed
```
The above calls `viz_peaks` on KLF4 transcription factor generated by HOMER's `findPeaks`.

```
peaksense viz_peaks examples/Klf4.peaksense.bed
```
The above calls `viz_peaks` on KLF4 transcription factor generated by PeakSense's `peaksense`.


## Issues and Contributions
If you encounter any issues while using PeakSense or have suggestions for improvements, please create an issue on the GitHub repository. Contributions are also welcome through pull requests.

## License
PeakSense is licensed under the MIT License. See LICENSE for more information.

## Acknowledgments
We would like to thank the developers of HOMER for their valuable work, which inspired PeakSense.

## Contact
For any further questions or inquiries, please contact eric@internalize.io.
