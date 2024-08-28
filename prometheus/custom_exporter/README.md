````````````
# idunaas custom exporter for prometheus


## Description: 
The purpose of this script is to check for UI availability for subsystems `EVNFM`, `ENM`, `EOCM`, check service availability of EOCM app running on Linux VMs and export them as metrics to prometheus server. And this metrics should also be available to IDUNAAS grafana platform for their monitoring and alerting.


## sample metrics exported for reference:
```
evnfm_ui_health_status{hostname="evnfm01.stsvp6accd01.stsoss.sero.gic.ericsson.se",httpscheck="0",logincheck="0",tcpcheck="0"} 0.0
enm_ui_health_status{hostname="stsvp6aenm01-136.stsoss.sero.gic.ericsson.se",httpscheck="0",logincheck="0",tcpcheck="0"} 0.0
eocm_ui_health_status{hostname="stsvp6aeocm01-197.stsoss.sero.gic.ericsson.se",httpscheck="0",logincheck="0",tcpcheck="0"} 0.0
eocm_sa_health_status{hostname="localhost"} 1.0
```

UI availability will have 4 labels: `hostname`, `httpscheck`(http check status), `tcpcheck`(tcp check status), and `logincheck`(UI login check).  The overall value is arrived based on the health check status result from tcpcheck, logincheck, and httpcheck. 
The value `0 is successful` and `1 is failure`. The success is only when all checks are passed and failure even if one check is failed.

Service availability check will have only 1 label which is `hostname`.  The overall status is based on the result obtained from the remote executing of the script `ecm_monitor.sh` which is available on the STS EOCM VM.

# Installation Instruction: 

## Install on kubernetes cluster.
Pre-requisite:
Prometheus server should be running already and the custom exporter should be installed on the same access network.

If the cluster is able to access the repository `armdocker.rnd.ericsson.se/proj-idun-aas` then you can install it using helm chart on the prometheus namespace.

```bash 
helm upgrade --install idunaas-custom-exporter idunaas-custom-exporter -n prometheus
```

If the cluster is not able to access the idunaas project docker repository then you need to build the image from Dockerfile, tag it and then push it to the repository that your cluster have access.  Update the helm chart values to pick the image from the right repository. Once the configuration is complete, proceed with installing using helm install command.

Clone the idunaas custom exporter code to your local

```bash 
docker build -t idunaas-custom-exporter:<<version>> <<context>>
docker tag idunaas-custom-exporter:<<version>> <<repo>>/idunaas-custom-exporter:<<version>>
docker push <<repo>>/idunaas-custom-exporter:<<version>>
```

helm install or upgrade command with dry run to verify the configuration.
```bash
helm upgrade --install idunaas-custom-exporter idunaas-custom-exporter -n prometheus --dry-run --debug
```

helm install or upgrade command without dry run to apply the configuration to the environment.
```bash
helm upgrade --install idunaas-custom-exporter idunaas-custom-exporter -n prometheus
```
## 2. Install on Virtual machine,
 Prequisites:
```bash 
docker should be already installed.
```
if the idunaas docker repo is not accessible. The follow the above instructions to build and run the container with below command. 

You can pass the environment variable separately with `-e name=value` or configure all env in single file and pass the file as below during the run
```bash
docker run --env-file <<envfilename>> -p 8008:8008 armdocker.seli.gic.ericsson.se/proj-idun-aas/idunaas-custom-exporter:<<version>>
# or 
Execute docker-compose up command using the compose file. Make sure the environment variable in the compose file is correct.
docker-compose up
```````````````
