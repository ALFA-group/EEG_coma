
# coding: utf-8

# In[9]:


from collections import defaultdict
import re
import utils


# In[10]:


def write_list(l, fn):
    with open(fn, 'w') as f:
        for i, x in enumerate(l):
            if i!=0:
                f.write('\n')
            f.write(x)


# In[11]:


def read_list(fn):
    list_ = []
    with open(fn, 'r') as f:
        for l in f.readlines():
            list_.append(l.strip())
    return list_


# # Exclude_sids.txt

# In[12]:


exclude_patient_names = read_list('/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/exclude_patient_sids.txt')


# # All_all.txt

# ### Create list of all our patients, and {patient:[edfs]}

# In[13]:


our_patients = set([])
all_edfs = read_list('/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/all_all.txt')
patient_to_edfs = defaultdict(list)
for edf in all_edfs:
    patient = utils.get_pt_from_edf_name(edf)
    our_patients.add(patient)
    edf_fn = edf.split('/')[-1]
    patient_to_edfs[patient].append(edf_fn)
our_patients = list(our_patients)
our_patients.sort(key=utils.parse_patient_name)
patient_to_edfs = dict(patient_to_edfs)


# In[14]:


#write_list(our_patients, '/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/all_patient_names.txt')


# # Master Lookup

# ### List of all sids

# In[15]:


import pandas as pd


# In[19]:


lookup = pd.read_csv('/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/master_lookup.csv')
sids = lookup['sid']
master_patient_names = list(set(sids.tolist()))
master_patient_names = [p for p in master_patient_names if type(p)==str] # get rid of nan


# In[20]:


master_patient_names.sort(key=utils.parse_patient_name)


# In[21]:


write_list(master_patient_names, '/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/all_new_patient_names.txt')


# ### Create mapping from sid to Y/N should be included or not

# In[24]:


import numpy as np


# In[27]:


sid_to_yn = {}
for i, row in lookup.iterrows():
    sid, yn = row['sid'], row['master_match']
    if pd.isnull(sid):
        continue
    assert(yn=='Y' or yn=='N'), 'yn not Y or N'
    if sid in sid_to_yn:
        assert(sid_to_yn[sid]==yn), "one sid with more than one yn"
    else:
        sid_to_yn[sid]=yn


# ### Create mapping from sid to edfs

# In[ ]:


lookup = pd.read_csv('/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/master_lookup.csv')
sid_to_edfs = defaultdict(list)
for i, row in lookup.iterrows():
    sid, fn = row['sid'], row['new_filename']
    if pd.isnull(sid):
        continue
    sid_to_edfs[sid].append(fn)
sid_to_edfs = dict(sid_to_edfs)


# ### Check sid, studyID, and id...

# In[31]:


for i, row in lookup.iterrows():
    full_sid, studyid, id_ = row['sid'], row['StudyID'], row['ID']
    if pd.isnull(full_sid):
        if pd.isnull(studyid):
            print(row)
        else:
            print('sid {}, studyid {}, id {}'.format(full_sid, studyid, id_))
        continue
    try:
        id_ = int(id_)
        studyid = int(studyid)
        sid = utils.parse_out_patient_id(full_sid)
    except:
        print('0 sid={}, studyid={}, id={}'.format(full_sid, studyid, id_))        
    if sid==studyid and sid==id_:
        # normal case
        continue
    if sid!=studyid and studyid==id_:
        # expect this case for 'bwh'
        if 'bwh' in full_sid:
            # normal
            #print('1 sid={}, studyid and id={}'.format(full_sid, studyid))
            pass
        else:
            print('!!!!!!!!!1 sid={}, studyid and id={}'.format(full_sid, studyid))
    if sid==studyid and studyid!=id_:
        print('2 sid, studyid={}, id={}'.format(full_sid, id_))
    if sid==id_ and studyid!=sid:
        if 'bi' in full_sid:
            pass
        else:
            print('!!!!!!3 sid, id={}, studyid={}'.format(full_sid, studyid))
    if sid!=studyid and sid!=id_ and id_!=studyid:
        print('4 sid={}, studyid={}, id={}'.format(full_sid, studyid, id_))


# ### Get list of patients which are skipped in master_patient_names

# In[32]:


def get_skipped_patients(patient_list):
    hosp_to_max_id = {'ynh':1, 'bi':1, 'mgh':1, 'bwh':1}
    for sid in patient_list:
        hosp, pid = utils.parse_patient_name(sid)
        hosp_to_max_id[hosp]= max(hosp_to_max_id[hosp], pid) 
    skipped_patients = []
    for hosp in ['ynh', 'bi', 'mgh', 'bwh']:
        for i in range(1, hosp_to_max_id[hosp]+1):
            sid = '{}{}'.format(hosp, i)
            if sid not in patient_list:
                skipped_patients.append(sid)
    return skipped_patients


# In[34]:


skipped_patients = get_skipped_patients(master_patient_names)
skipped_patients_master = skipped_patients
sure_skipped_patients = []
maybe_skipped_patients = []
for pt in skipped_patients:
    hosp, pid = utils.parse_patient_name(pt)
    if hosp=='bwh' and pid >= 143:
        # can't tell if actually is a skip, because bwh numbers jump weirdly
        maybe_skipped_patients.append(pt)
    else:
        sure_skipped_patients.append(pt)


# In[38]:


write_list(maybe_skipped_patients, "maybe_skipped_master.txt")
write_list(sure_skipped_patients, "sure_skipped_master.txt")


# ## Get list of patients in outcomes excel

# In[1]:


outcomes_df = pd.read_csv('/afs/csail.mit.edu/u/t/tzhan/eeg/coma_EEG_alice_zhan/patient_outcome_info/new_outcomes.csv')
outcomes_patient_names = outcomes_df['sid'].tolist()
outcomes_patient_names = sorted(outcomes_patient_names, key=utils.parse_patient_name)


# In[ ]:


#write_list(outcomes_patient_names, '/Users/tzhan/src/coma_EEG_alice_zhan/patient_outcome_info/patients_with_outcomes.txt')


# ### Get list of patients which are skipped in outcomes_patient_names

# In[94]:


skipped_patients_outcomes = get_skipped_patients(outcomes_patient_names)


# # Comparing outcomes list and master list
# 
# #### Outcomes list is a SUBSET of master list
# #### Skipped list for master is a subset of skipped list for outcomes

# In[99]:


outcomes_set = set(outcomes_patient_names)
master_set = set(master_patient_names)
print outcomes_set.difference(master_set)
print master_set.difference(outcomes_set)


# In[98]:


skipped_patients_master==skipped_patients_outcomes
skipped_o_set = set(skipped_patients_outcomes)
skipped_m_set = set(skipped_patients_master)
print skipped_o_set.difference(skipped_m_set)
print skipped_m_set.difference(skipped_o_set)


# ## Other

# In[1]:


def convert_old_name_to_new_format(patient, edf_style=False):
    hosp_mapping = {'CA_BIDMC':'bi', 'CA_MGH':'mgh', 'ynh':'ynh', 'bwh':'bwh'}
    hosp, pid = utils.parse_patient_name(patient)
    new_hosp = hosp_mapping[hosp]
    if edf_style:
        return '{}_{}'.format(new_hosp, pid)
    return '{}{}'.format(new_hosp, pid)


# In[17]:


mapping = {'bwh_1605' : 'bwh211', 'bwh_1636':'bwh210', 'bwh_1639':'bwh212', 'bwh_1641':'bwh213'}


# In[36]:


def guess_corresponding_id(patient):
    if patient in mapping:
        return mapping[patient]
    new_fmt = convert_old_name_to_new_format(patient)
    return new_fmt


# In[ ]:


def extract_and_underscore_timestamp(our_edf_name):
    # extracts out timestamp from our edf
    # if uses T instead of '_', as with bwh and ynh, return with '_'
    match_obj = re.search('_(\d+(_|T)\d+).edf', our_edf_name)
    if match_obj is None:
        print "WARNING: FILE NAME IS WEIRD"
        return our_edf_name
    ts = match_obj.group(1)
    ts = ts.replace('T', '_')
    chunks = ts.split('_')
    if (len(chunks[0])!=8 or len(chunks[1])!=6):
        print "WARNING: ts weird {}".format(ts)
    return ts


# In[146]:


def seem_similar(master_edfs, our_edfs, vb=False):
    if len(master_edfs)!=len(our_edfs):
        if vb:
            print('lens not equal, len(master)={}, len(our)={}'.format(len(master_edfs), len(our_edfs)))
        return False
    num_not_matching = 0
    master_timestamps = [extract_and_underscore_timestamp(master_edf) for master_edf in master_edfs]
    master_timestamps_sans_last_two_digits = [ts[:-2] for ts in master_timestamps]
    for our_edf in our_edfs:
        ts = extract_and_underscore_timestamp(our_edf)
        ts_sans_last_two_digits = ts[:-2]
        if ts_sans_last_two_digits not in master_timestamps_sans_last_two_digits:
            # no matching master timestamp
            if vb:
                print('ts with no match {}'.format(ts))
            num_not_matching +=1
    if (num_not_matching+0.0)/len(our_edfs) <= 0.25:
        return True
    if vb:
        print '{} out of {} ts without match'.format(num_not_matching, len(our_edfs))
    return False


# ### Collect list of matchings which won't be verified as matches by seem_similar

# In[147]:


our_patient_to_guess_id_exceptions = [
    ('CA_BIDMC_20', 'bi20')   # len(our_edf)==1 but matches with one of the many master ones
]


# ### Check status of all patients:
# #### Do they having a matching new sid?
# ##### If so: does it have a 'Y'? does it have outcome? is it in exclude list?
# #### If no matching new sid, 
# ##### Is it because the corresponding new sid was skipped? Or is it an old sid?

# In[152]:


for patient in our_patients:
    print('\nANALYZING PATIENT {}'.format(patient))
    guess_id = guess_corresponding_id(patient)
    hosp, id_ = utils.parse_patient_name(patient)
    if guess_id in master_patient_names:
        yn = sid_to_yn[guess_id]
        master_edfs = sid_to_edfs[guess_id]
        our_edfs = patient_to_edfs[patient]
        if ((patient, guess_id) in our_patient_to_guess_id_exceptions or 
            seem_similar(master_edfs, our_edfs)):
            print('seems like good matching', patient, guess_id)
            sid = guess_id
            if yn=='Y' and sid in outcomes_patient_names and sid not in exclude_patient_names:
                print('PERFECT! Y in master, has outcome, and not in exclude')
            else:
                if yn!='N':
                    print('YN={}'.format(yn))
                if sid not in outcomes_patient_names:
                    print('sid not in outcomes')
                if sid in exclude_patient_names:
                    print('in exclude list')
        else:
            print('guess id and patient id did not match', patient, guess_id, master_edfs, our_edfs)
            # since no match, we cannot say if patient is excluded, has outcome, etc.
            
    else:
        print('guess id not in master', patient, guess_id)
        # since no match, we cannot say if patient is excluded, has outcome, etc.
        # but maybe it is a skipped one in master because it is skipped in outcome?


# In[ ]:


# for patient in our_patients:
#     standardized = standardize_patient_name(patient)
#     if standardized not in master_patient_names:
#         if patient in mapping:
#             if mapping[patient] not in master_patient_names:
#                 print patient, standardized
#         else:
#             print patient, standardized


# In[ ]:


bwh_lookup = lookup.loc[lookup['site'] == 'bwh']
bwh_studyids = set(bwh_lookup['StudyID'].tolist())
bwh_sids = set(bwh_lookup['sid'].tolist())
bwh_sids.remove(np.nan)
bwh_studyids.remove(np.nan)
bwh_studyids = set(['bwh'+id_ for id_ in bwh_studyids])


# In[ ]:


ambiguous = bwh_sids.intersection(bwh_studyids)


# In[ ]:


# mapping = {'bwh_1605' : 'bwh211', 'bwh_1636':'bwh210', 'bwh_1639':'bwh212', 'bwh_1641':'bwh213'}
# for patient in patients:
#     if patient in mapping:
#         continue
#     name = standardize_patient_name(patient)
#     if name not in master_patient_names:
#         print name


# In[ ]:


# our bwh118 -> skipped in master sids, and sid bwh118 in exclude list. 
# our bwh220 -> excluded because bwh220 and bwh220_old excluded
# our bwh221 -> bwh sids go up to 219, and 220 is excluded. 
        # is this new sid 221, excluded, or is it old sid 221, corresponding to new bwh90?
    

