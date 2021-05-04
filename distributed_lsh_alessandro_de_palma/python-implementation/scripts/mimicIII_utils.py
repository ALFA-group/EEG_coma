"""
    File containing scripts to handle the MIMICIII database.

    REQUIREMENTS: WFDB Python Toolbox [1]

    [1] https://pypi.python.org/pypi/wfdb
    [3] https://physionet.org/physiobank/database/mimic3wdb/, Technical Limitations
"""
import matplotlib
matplotlib.use('Agg')
import wfdb
import collections
import pickle
from math import floor
import matplotlib.pyplot as plt

class Segment():

    """
    Class containing raw segment information.
    """

    def __init__(self, length, record, types):

        self.length = length
        self.record = record  # Record stored as an integer.
        self.types = types  # List of signal types.


def get_waveforms_list():
    '''
    Read the list of waveforms from the file in [2], which is assumed to be stored in this folder
    under the name "RECORDS-waveforms"

    [2] https://physionet.org/physiobank/database/mimic3wdb/RECORDS-waveforms

    :return: list of (folder, record) pairs.
    '''

    filename = "RECORDS-waveforms"

    records = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split("/")

            folder = linesplit[0]
            record = linesplit[1]
            records.append((folder, record))

    return records


def is_segment(filename):
    """
    Check whether a MIMIC file is a proper segment (from the name).

    :param filename: the name of the file
    :return: True if the file is a segment, False otherwise.
    """

    output = True

    if filename == "~":
        output = False

    splits = filename.split("_")
    if len(splits) >= 2:
        if splits[1] == "layout":
            output = False

    return output


def pickle_ECG_headers():

    """
    Scan the dataset to build a list of Segments (containing length, record and types).
    Then pickle it to "mimicIII-headers-dict.pickle".

    This is done through dataset header files.
    Useful fields:
        siglen - integer signal length in terms of samples (there's 125 samples per second, as 'fs' can testify)
        signame - list of signal types. Accepted ECG types are stored in a dictionary.
        segname - list of segment names, contained in a record's header.

    :return: nothing.
    """

    ECG_types = {"I", "II", "III", "AVR", "AVL", "AVF", "V", "V1", "V2", "V3", "V4", "V5", "MLI", "MLII", "MLIII", "ABP"}
    ECG_list = []

    waveforms = get_waveforms_list()

    for cpair in waveforms:

        folder = cpair[0]
        record = cpair[1]

        record_header = wfdb.rdheader(record, pbdir='mimic3wdb/{}/{}/'.format(folder, record))
        segments = record_header.segname

        for segment in segments:
            if is_segment(segment):
                # Read segment's header file.
                print(segment)
                segment_header = wfdb.rdheader(segment, pbdir='mimic3wdb/{}/{}/'.format(folder, record))
                # Append signal lengths.
                ctypes = set(segment_header.signame)
                cintersection = ctypes.intersection(ECG_types)
                if bool(cintersection):  # If nonempty intersection.
                    ECG_list.append(Segment(segment_header.siglen, int(record), cintersection))

    with open('mimicIII-headers-list.pickle', 'wb') as file:
        pickle.dump(ECG_list, file)


def count_ECG_signals():
    """
    Computes statistics on the MIMIC ECG database.
    Assumes pickle_ECG_headers has already been called and the dictionary is available.

    :return: nothing
    """

    ABP = {"ABP"}
    # Dictionary of available ECG types.
    ECG_types = {"I", "II", "III", "AVR", "V"}
    ECG_types_list = list(ECG_types)
    type_to_int = {}
    for i in range(len(ECG_types_list)):
        type_to_int[ECG_types_list[i]] = i

    signal_types = ECG_types.union(ABP)
    # Type-associated counters.
    counter_10min = {}  # Number of segments of length 10min.
    counter_30min = {}  # Number of segments of length 30min.
    counter_300min = {}  # Number of segments of length 300min.
    # Length thresholds.
    th_10min = 125 * 60 * 10
    th_30min = 125 * 60 * 30
    th_300min = 125 * 60 * 300

    # Patient info: number of 10min segments per patient.
    patient_counter = {}

    for type in signal_types:
        counter_10min[type] = 0
        counter_30min[type] = 0
        counter_300min[type] = 0
        patient_counter[type] = collections.defaultdict(int)  # Initialize all possible patient counters to 0.

    # Type matching info.
    matched_counter = []
    for i in range(len(ECG_types_list)):
        matched_counter.append([])

        for j in range(len(ECG_types_list)):
            if j >= i:
                break

            matched_counter[i].append(0)

    # Read from pickle.
    with open('mimicIII-headers-list.pickle', 'rb') as f:
        ECG_header_list = pickle.load(f)

        for segment in ECG_header_list:
            seg_types = segment.types
            cintersection = seg_types.intersection(signal_types)
            cECGintersection = seg_types.intersection(ECG_types)
            if bool(cintersection):
                for ctype in cintersection:
                    # Compute number of segments.
                    counter_10min[ctype] += floor(segment.length/th_10min)
                    counter_30min[ctype] += floor(segment.length / th_30min)
                    counter_300min[ctype] += floor(segment.length / th_300min)

                    # Compute the number of 10min segments per patient (assuming they correspond to records, see [3]).
                    patient_counter[ctype][segment.record] += floor(segment.length/th_10min)

            if bool(cECGintersection):
                for ctype in cECGintersection:
                    # Compute 2-way matchings.
                    i = type_to_int[ctype]
                    for j in range(len(ECG_types_list)):
                        if j >= i:
                            break
                        if ECG_types_list[j] in cECGintersection:
                            matched_counter[i][j] += floor(segment.length/th_10min)

    figure_num = 0
    for type in signal_types:
        print("{}, number of 10min segments: {}".format(type, counter_10min[type]))
        print("{}, number of 30min segments: {}".format(type, counter_30min[type]))
        print("{}, number of 300min segments: {}".format(type, counter_300min[type]))
        print("{}, number of patients: {}".format(type, len(patient_counter[type].keys())))
        print("")

        # Plot patient histogram.
        plt.figure(figure_num)
        plt.hist(list(patient_counter[type].values()), normed=False, bins=300, range=[0, 2000])
        plt.title("{}, distribution of the number of 10min segments per patient".format(type))
        plt.savefig("{}-patients-histogram".format(type))
        figure_num += 1

    print("")
    for i in range(len(ECG_types_list)):
        for j in range(len(ECG_types_list)):
            if j >= i:
                break
            print("{}+{}, number of 10min segments: {}".format(ECG_types_list[i], ECG_types_list[j], matched_counter[i][j]))

    return


def write_dataset_to_file(filename, type, length):

    """
    Write a preprocessed dataset with a given segment length to a given file.
    The file format is one row of space-separated values for each point.

    :param filename: the file's name.
    :param type: the signal type (e.g., "ABP").
    :param length: the number of samples each segment is made of.

    :return: nothing
    """

    ECG_lists = collections.defaultdict(list)

    waveforms = get_waveforms_list()

    for cpair in waveforms:

        folder = cpair[0]
        record = cpair[1]

        record_header = wfdb.rdheader(record, pbdir='mimic3wdb/{}/{}/'.format(folder, record))
        segments = record_header.segname

        for segment in segments:
            if is_segment(segment):
                # Read segment's header file.
                print(segment)
                # TODO: change to read content.
                segment_content = wfdb.rdheader(segment, pbdir='mimic3wdb/{}/{}/'.format(folder, record))

                #TODO: preprocess and slice on the go, we have no space for the whole thing.
                if type == "ABP":
                    pass

                #TODO: once I have the segment, just append it to file.



if __name__ == "__main__":

    count_ECG_signals()
    #pickle_ECG_headers()
