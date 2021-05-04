"""
    File containing scripts to setup the nodes (move files, install requirements, etc.).
"""
import os

def create_openstack_instances():

    #TODO: for preliminary testing, the instances are created by hand and it is assumed that the installation commands have been performed already.
    #TODO: in the future something automating it might come handy (look at cCube's orchestrator's code).

    '''
    List of commands to execute to install the package on a newly created Ubuntu16.04LTS node on OpenStack.

    on remote machine:
    mkdir code; cd code; mkdir distributed_SLSH
    mkdir results; cd results; mkdir intranode (or "distributed", on the middleware)

    on local machine:
    scp -r -i ~/.ssh/openstack.key ../distributed_SLSH/* ubuntu@128.52.176.57:/home/ubuntu/code/distributed_SLSH/

    on remote machine:
    sudo apt-get -y install python3-setuptools; sudo apt-get update && sudo apt-get -y upgrade
    sudo apt-get -y install python3-pip
    cd code/distributed_SLSH; sudo python3 setup.py install


    IPs:
    middleware - 128.52.176.119
    nodes - "128.52.190.158", "128.52.190.159", "128.52.190.160", "128.52.190.161"
    '''

    return


def install_requirements(ip):
    """
    Install requirements, assumes the code is already on the machine, in folder ~/code/distributed_SLSH

    :param ip: the ip to install requirements on
    :return: nothing
    """

    print("Install requirements on node {}".format(ip))

    directory = "aledepo93"

    ssh = "ssh -i /home/{}/.ssh/openstack.key ubuntu@{} ".format(directory, ip)

    os.system(ssh + "\"sudo apt-get -y install python3-setuptools; sudo apt-get update && sudo apt-get -y upgrade\"")
    os.system(ssh + "\"sudo apt-get -y install python3-pip\"")
    os.system(ssh + "\"cd code/distributed_SLSH; sudo python3 setup.py install\"")
    os.system(ssh + "\"export LC_ALL=C; pip3 install scipy; pip3 install scikit-learn\"")


def create_folder_copy_code(ip, middleware=False):
    """
        Create the necessary folders on the remote machine and copy the local code there.

        :param ip: the ip to execute the above on
        :return: nothing
    """

    print("Create folder and copy code to node {}".format(ip))

    directory = "aledepo93"

    ssh = "ssh -i /home/{}/.ssh/openstack.key ubuntu@{} ".format(directory, ip)  # User settings.

    if middleware:
        results_folder = "middleware"  # User settings.
    else:
        results_folder = "intranode"  # User settings.

    os.system(ssh + "\"mkdir code; cd code; mkdir distributed_SLSH; mkdir results; cd results; mkdir {}\"".format(results_folder))

    os.system("scp -r -i /home/aledepo93/.ssh/openstack.key ../distributed_SLSH/* ubuntu@{}:/home/ubuntu/code/distributed_SLSH/".format(ip))  # User settings.

    # On middleware, copy scripts too.
    if middleware:
        os.system(ssh + "\"cd code; mkdir scripts;\"")
        os.system("scp -r -i /home/aledepo93/.ssh/openstack.key ./* ubuntu@{}:/home/ubuntu/code/scripts/".format(ip))  # User settings.


if __name__ == "__main__":

    nodes = ["128.52.162.123"]  # User settings.
    middleware_ip = "128.52.176.119"  # User settings.

    for node in nodes:
        create_folder_copy_code(node)
        install_requirements(node)

    #create_folder_copy_code(middleware_ip, middleware=True)
    #install_requirements(middleware_ip)
