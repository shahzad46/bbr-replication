# Setup

Modified from https://github.com/google/bbr/blob/master/Documentation/bbr-quick-start.md

The experiment setup uses two Google cloud VMs running a modified linux kernel. We
provide a simple install script to create the VMs and install all needed
dependencies.

The script uses gcloud commandline tools, so first install those following the
instructions at: https://cloud.google.com/sdk/downloads 

Now login to a gcloud project:
```
gcloud auth login
```

By default, the script uses a new "bbr-replication" project for the VMs, but you
can change this by modifying `settings.sh`

Now clone this repo and run the script to create the VMs:
```
git clone https://github.com/bgirardeau/bbr-replication
cd bbr-replication
# This script will take roughly 20-30 minutes to complete.
# You may need to interact with 1 or 2 prompts at the beginning when launching
# the VMs
bash create_vms.sh
```

Run the experiments:
```
# This will run all the three experiments with vm-vm and mininet setup. 
# At the end of this experiment, the figures will be in the folder ./figures/
bash ./run_experiments.sh 
```
