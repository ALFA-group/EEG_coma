
# coding: utf-8

# In[1]:


from __future__ import print_function
import os
import sys


# In[2]:


def get_patient_files(patient_filepath):
    # returns all eeg files for patient
    # patient_filepath is path to file containing list 
    # of all eeg files associated with patient
    eeg_files = []
    for line in open(patient_filepath):
        eeg_file = line.strip()
        eeg_files.append(eeg_file)
    return eeg_files


# In[3]:


def get_all_files(patients_dir):
    # returns list of all files for all patients
    patient_filepaths = []
    for dir_ in os.walk(patients_dir):
        filenames = dir_[2]
        dirpath = dir_[0]
        for filename in filenames:
            patient_filepath = os.path.join(dirpath, filename)
            patient_filepaths.append(patient_filepath)
    all_files = []
    for patient_filepath in patient_filepaths:
        all_files += get_patient_files(patient_filepath)
    return all_files


# In[4]:


def create_patient_all_files_list(patients_dir, output_file):
    all_files = get_all_files(patients_dir)
    output = open(output_file, 'w')
    for file_ in all_files:
        print(file_, file=output)


# In[5]:


if __name__ == "__main__":

    # Input format: patients_dir output_file

    patients_dir = sys.argv[1]
    output_file = sys.argv[2]

    create_patient_all_files_list(patients_dir, output_file)

