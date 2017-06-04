# Setup

Modified from https://github.com/google/bbr/blob/master/Documentation/bbr-quick-start.md

Install gcloud command line tools following the instructions at: 
https://cloud.google.com/sdk/downloads 

Out setup requires installing a modified linux kernel and creating up two customes vms. 
gcloud commandline tools are required so that you can run our simple install script.

Create a gcloud project:
```
gcloud auth login
gcloud create project bbr-replication 
gcloud config set project bbr-replication
--- add billing  
```

Create the vms:
```
git clone https://github.com/bgirardeau/bbr-replication
cd bbr-replication
# This script will take roughly 20-30 minutes to complete. 
bash ./create_vms.sh
```
Run the experiments:
```
# This will run all the three experiments with vm-vm and mininet setup. 
# At the end of this experiment, the figures will be in the folder ./figures/
bash ./run_experiments.sh 
```
