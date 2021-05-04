import os

def read_head_chars(filename, N):
    num_chars_read = 0
    chars = []
    with open(filename, encoding="Latin-1") as f:
        while True:
            c = f.read(1)
            chars.append(c)
            num_chars_read += 1
            if not c or num_chars_read > N:
                break
    return ''.join(chars)

#### CHANGE THIS LINE TO THE LOCATION OF THE EEG DATASET FOLDER #####
dataset_directory = 'B:\Projects\CARDIAC_ARREST_DATA\ICARE_EDFs'
#dataset_directory = '/afs/csail.mit.edu/u/t/tzhan/NFS/EEG-dataset/'
header_dataset_directory = '.'
#hosps = ['outboxMGH_BWH/MGH', 'outboxMGH_BWH/BWH', 'outboxBIDMC', 'outboxYALE']
hosps = ['MGH', 'BWH', 'BIDMC', 'YALE']
ignore_hosps = ['UTW', 'ULB']
####################################################################

if not os.path.isdir(header_dataset_directory):
    os.makedirs(header_dataset_directory)

for hosp in hosps:
    hosp_directory = os.path.join(dataset_directory, hosp)
    for dirpath, subdirs, filenames in os.walk(hosp_directory):
        for fn in filenames:
            _, ext = os.path.splitext(fn)
            if ext != '.edf':
                continue
            path_within_hosp_dir = os.path.relpath(dirpath, hosp_directory)
            if path_within_hosp_dir =='.':
                new_header_file_dir = os.path.join(header_dataset_directory, hosp)
            else:
                new_header_file_dir = os.path.join(header_dataset_directory, hosp, path_within_hosp_dir)
            if not os.path.isdir(new_header_file_dir):
                os.makedirs(new_header_file_dir)
            new_header_file_path = os.path.join(new_header_file_dir, fn)
            full_orig_edf_path = os.path.join(dirpath, fn)
            chars = read_head_chars(full_orig_edf_path, 6000)
            print('Writing to ', new_header_file_path)
            print('Writing header ', chars[100:200])
            with open(new_header_file_path, 'w') as f:
                f.write(chars)