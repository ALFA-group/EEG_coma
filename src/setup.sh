# setup script for csail-ubuntu instances
# assumes NFS folder already exists in my home dir
sudo apt update
sudo apt install -y nfs-common
sudo apt install -y git
sudo mount nfs-prod-1.csail.mit.edu:/export/evodesignopt/slc /afs/csail.mit.edu/u/t/tzhan/NFS
