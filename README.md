# Setup

Modified from https://github.com/google/bbr/blob/master/Documentation/bbr-quick-start.md

```
typeset -x PROJECT="bbr-replication"  # An existing GCE project name
typeset -x ZONE="us-west1-a"          # Any GCE Zone
gcloud compute instances create "bbrtest1" \
    --project ${PROJECT} \
    --zone ${ZONE} \
    --machine-type "n1-standard-8" \
    --network "default" \
    --maintenance-policy "MIGRATE" \
    --boot-disk-type "pd-standard" \
    --boot-disk-device-name "bbrtest1" \
    --image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1604-xenial-v20170502" \
    --boot-disk-size "20" \
    --scopes default="https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly"
gcloud compute ssh --project ${PROJECT} --zone ${ZONE} bbrtest1
```
