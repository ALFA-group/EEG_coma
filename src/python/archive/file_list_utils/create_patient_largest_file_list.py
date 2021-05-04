
# coding: utf-8

# In[1]:


from __future__ import print_function
import os
import sys


# In[2]:


def get_largest_eeg_file(patient_filepath):
    # returns largest eeg file for patient
    # patient_filepath is path to file containing list 
    # of all eeg files associated with patient
    largest_eeg_file = None
    largest_eeg_filesize = 0
    for line in open(patient_filepath):
        eeg_file = line.strip()
        size = os.path.getsize(eeg_file)
        if size > largest_eeg_filesize:
            largest_eeg_filesize = size
            largest_eeg_file = eeg_file
    return largest_eeg_file


# In[3]:


def get_largest_eeg_files(patients_dir):
    # returns list of largest eeg files for all patients
    patient_filepaths = []
    for dir_ in os.walk(patients_dir):
        filenames = dir_[2]
        dirpath = dir_[0]
        for filename in filenames:
            patient_filepath = os.path.join(dirpath, filename)
            patient_filepaths.append(patient_filepath)
    largest_files = [get_largest_eeg_file(patient_filepath) for patient_filepath in patient_filepaths]
    return largest_files


# In[4]:


def create_patient_largest_file_list(patients_dir, output_file):
    largest_files = get_largest_eeg_files(patients_dir)
    output = open(output_file, 'w')
    for file_ in largest_files:
        print(file_, file=output)


# In[5]:


if __name__ == "__main__":

    # Input format: patients_dir output_file

    patients_dir = sys.argv[1]
    output_file = sys.argv[2]

    create_patient_largest_file_list(patients_dir, output_file)

