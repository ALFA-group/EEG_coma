import os

to_split_fn = '/afs/csail.mit.edu/u/t/tzhan/eeg/patient_file_lists/largest/patient_largest_files_whole.txt'
output_fn = '/afs/csail.mit.edu/u/t/tzhan/eeg/patient_file_lists/largest/hosp_largest_files.txt'
# Number of files to split each hospital into
split_n = 2

def chunkIt(seq, num):
# split list into 'n' equal parts
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def write_splits(hospital_files, hospital_name):
    splits = chunkIt(hospital_files, split_n)
    for i, split in enumerate(splits):
        filepath = output_fn.replace('hosp', '{}{}'.format(hospital_name, i))
        with open(filepath, 'w') as f:
            for line in split:
                f.write(line)

with open(to_split_fn) as f:
    lines = f.readlines()

mgh = []
bi = []
yale = []
bwh = []

for line in lines:
    if 'CA_MGH' in line:
        mgh.append(line)
    elif 'CA_BIDMC' in line:
        bi.append(line)
    elif 'ynh' in line:
        yale.append(line)
    elif 'bwh' in line:
        bwh.append(line)
    else:
        print 'not a proper edf', line

write_splits(mgh, 'mgh')
write_splits(bi, 'bi')
write_splits(yale, 'yale')
write_splits(bwh, 'bwh')

