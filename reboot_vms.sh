source settings.sh
gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME1} \
    --command 'sudo reboot now'
gcloud compute ssh --project ${PROJECT} --zone ${ZONE} ${NAME2} \
    --command 'sudo reboot now'

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
