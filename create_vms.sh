source settings.sh

create_project() {
    gcloud projects create $PROJECT
}

make_vm() {
    NAME=$1
    PROJECT=$2
    ZONE=$3

    echo "Creating VM $NAME"
    gcloud compute instances create "$NAME" \
	--project "$PROJECT" \
	--zone "$ZONE" \
	--machine-type "n1-standard-4" \
	--network "default" \
	--maintenance-policy "MIGRATE" \
	--boot-disk-type "pd-standard" \
	--boot-disk-device-name "$NAME" \
	--image "https://www.googleapis.com/compute/v1/projects/ubuntu-os-cloud/global/images/ubuntu-1604-xenial-v20170502" \
	--boot-disk-size "30" \
	--scopes default="https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly"
    made_vm=$?

    echo "Copying files to $NAME"
    until gcloud compute ssh --project $PROJECT --zone $ZONE $NAME --command "mkdir -p bbr-replication"
    do
	if [ made_vm ];
	then
	    echo "Waiting for ssh key to propagate to $NAME..."
	    sleep 2
	else
	    break
	fi
    done;
    gcloud compute copy-files --project $PROJECT --zone $ZONE * $NAME:~/bbr-replication
}


upgrade_kernel() {
    NAME=$1
    PROJECT=$2
    ZONE=$3

    echo "Installing kernel on $NAME"
    gcloud compute ssh --project $PROJECT --zone $ZONE $NAME --command "cd ~/bbr-replication && bash install_kernel.sh"
}

install_deps() {
    NAME=$1
    PROJECT=$2
    ZONE=$3

    echo "Installing dependencies on $NAME"
    gcloud compute ssh --project $PROJECT --zone $ZONE $NAME --command "cd ~/bbr-replication && bash install_deps.sh"
}

link_vms() {
    NAME1=$1
    NAME2=$2
    PROJECT=$3
    ZONE=$4

    gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME1} \
	--command 'cat ~/.ssh/id_rsa.pub' | \
	gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME2} \
	--command 'cat >> ~/.ssh/authorized_keys'

    gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME2} \
	--command 'hostname -I' | \
	gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME1} \
	--command 'cat > ~/.bbr_pair_ip'
}

wait_for_reboots() {
    NAME1=$1
    NAME2=$2
    PROJECT=$3
    ZONE=$4

until gcloud compute ssh --project $PROJECT --zone $ZONE $NAME1 --command "echo $NAME1 Rebooted!"
do
    echo "Waiting for $NAME1 to reboot..."
    sleep 2
done;

until gcloud compute ssh --project $PROJECT --zone $ZONE $NAME2 --command "echo $NAME2 Rebooted!"
do
    echo "Waiting for $NAME2 to reboot..."
    sleep 2
done;
}

# Comment out completed steps

#create_project

make_vm ${NAME1} ${PROJECT} ${ZONE}
make_vm ${NAME2} ${PROJECT} ${ZONE}

upgrade_kernel ${NAME1} ${PROJECT} ${ZONE}
upgrade_kernel ${NAME2} ${PROJECT} ${ZONE}

wait_for_reboots ${NAME1} ${NAME2} ${PROJECT} ${ZONE}

install_deps ${NAME1} ${PROJECT} ${ZONE}
install_deps ${NAME2} ${PROJECT} ${ZONE}

link_vms ${NAME1} ${NAME2} ${PROJECT} ${ZONE}
