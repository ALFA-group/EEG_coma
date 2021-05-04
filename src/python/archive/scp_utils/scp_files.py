from __future__ import print_function
import pexpect
import random
import sys

server = "128.52.176.155"
global_pword = "fillmein!!"

def scp(from_file_path, to_file_path, password=None):
    print(from_file_path)
    if password is None:
        password = global_pword
    try:
        command = "scp tzhan@{}:{} {}".format(server, from_file_path, to_file_path)
        #make sure in the above command that username and hostname are according to your server
        child = pexpect.spawn(command)
        expect_list = ["Password:", "(\d{1,3})%", pexpect.EOF]
        i = child.expect(expect_list)
        percentage=None
        while True:
            if i==0: # send password     
                child.sendline(password)
                i = child.expect(expect_list)
            elif i==1:
                percentage_str = child.after
                new_percentage = int(percentage_str[:-1])
                if percentage is None or new_percentage!=percentage:
                    percentage = new_percentage
                    if percentage % 10 == 0:
                        print(percentage_str, end='')
                    else:
                        print('.', end='')
                i = child.expect(expect_list)
            elif i==2:
                if percentage==100:
                    print("EOF")
                else:
                    print(child.before, child.after)
                break

    except Exception as e:
        print(e)
        
def scp_edf(edf_file, password):
    # get a file from remote by the edf name
    to_file_path = '/Users/tzhan/src/thesis/sample_data/scp_target'

    all_files_remote_path = '/afs/csail.mit.edu/u/t/tzhan/eeg/patient_file_lists/all_all.txt'
    all_files_local_path = '/Users/tzhan/tmp/to_scp_list.txt'
    scp(all_files_remote_path, all_files_local_path, password)
    with open(all_files_local_path) as f:
        for line in f.readlines():
            if edf_file in line:
                remote_edf_path = line.strip()

    scp(remote_edf_path, to_file_path, password)
        
if __name__ == "__main__":

    edf_file = sys.argv[1]
    if len(sys.argv)>2:
        password = sys.argv[2]
    else:
        password = None
    scp_edf(edf_file, password)
