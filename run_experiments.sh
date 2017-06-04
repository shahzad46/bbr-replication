source settings.sh

run_experiments() {
    NAME=$1
    PROJECT=$2
    ZONE=$3

    echo "Running all experiments"
    #gcloud compute ssh --project $PROJECT --zone $ZONE $NAME --command "cd ~/bbr-replication && bash create_figures.sh"
    gcloud compute scp --recurse --project $PROJECT --zone $ZONE $NAME:~/bbr-replication/figures ./
}

run_experiments ${NAME1} ${PROJECT} ${ZONE}
