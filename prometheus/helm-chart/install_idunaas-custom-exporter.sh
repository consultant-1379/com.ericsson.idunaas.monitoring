#!/bin/bash


function usage {
    echo ""
    echo "Usage:
        $0 <deployment_service_folder> <ci_folder> [<env_list>] [template]

        Paramters:
        - <deployment_service_folder>: this is the path in the filesystem where
                                       the Git repo of the deployment_service
                                       has been cloned. The project on Gerrit is
                                       'com.ericsson.idunaas.deployment_service'
        - <ci_folder>: this is the path in the filesystem where the Git repo of
                       the CI repo has been cloned. The project on Gerrit is
                       'com.ericsson.idunaas.ci'
        - <env_list>: Optional parameter. If missing install in all environments.
                      If given, this is the environment names where to install
                      the custom exporter.

                      If empty the custom exporter will be installed in all
                      environments. Otherwise this parameter will contain
                      the list of the environments (comma separated list).
                      Ex. bmasidun01,ernidun01,idunaasdev02
        - template: if the word 'template' is given after the environment list
                    then the output of the command 'helm template' will be
                    shown and no upgrade will be performed.

    "
}

test -z "$1" && \
    echo "Error: Deployment Service folder not provided" && \
    usage && \
    exit -1

test -z "$2" && \
    echo "Error: CI folder not provided" && \
    usage && \
    exit -2

HELMCHART_FOLDER="$(realpath ${1})/monitoring/prometheus/helm-chart"
DEPLOYMENTS_FOLDER="$(realpath ${2})/deployments"

BLACKLIST='-e conf-files -e infoveiap01 -e azeiapaasdev'
[ -z "$3" ] \
    && ENV_LIST=$(ls "$DEPLOYMENTS_FOLDER" | grep -v $BLACKLIST) \
    || ENV_LIST="$(echo -n $3 | tr , ' ')"

HELM_OPERATION="upgrade --install"
[ "$4" == "template" ] && \
    echo "No upgrade will be performed. Only template will be compiled and printed" && \
    HELM_OPERATION=template

test ! -e "$HELMCHART_FOLDER" && \
    echo "Error: the folder $HELMCHART_FOLDER does not exist." && \
    usage && \
    exit -3

test ! -e "$DEPLOYMENTS_FOLDER" && \
    echo "Error: the folder $DEPLOYMENTS_FOLDER does not exist." && \
    usage && \
    exit -4

### MAIN SCRIPT ###

NS=prometheus
KUBECONFIG=/tmp/kubeconfig

echo -e "\nThis script will install/upgrade the custom_exporter\n"

echo -n "Insert the password of 'appmgr-user': "
read APPMGR_PASSWD

cd "$HELMCHART_FOLDER"
for ENVNAME in $ENV_LIST; do
    echo "=== $ENVNAME ==="

    HELMCHART_VERSION=$( \
        grep 'version:' "$HELMCHART_FOLDER/idunaas-custom-exporter/Chart.yaml" \
        | cut -d : -f 2| tr -d ' ' \
    )

    if [ "$HELMCHART_VERSION" == "0.3.2" -o "$HELMCHART_VERSION" == "0.4.0" ]; then

        KUBECFGENV="$DEPLOYMENTS_FOLDER/$ENVNAME/workdir/kube_config/config"
        test ! -e "$KUBECFGENV" && echo "Skipping $ENVNAME because $KUBECFGENV does not exist" && continue
        APPMGR_CRT=$(find "$DEPLOYMENTS_FOLDER/$ENVNAME" | grep 'appmgr.*crt' || echo none)
        test ! -e "$APPMGR_CRT" && echo "Skipping $ENVNAME because APPMGR cert does not exist" && continue
        NAMESPACE=`cat $DEPLOYMENTS_FOLDER/conf-files/$ENVNAME.conf | grep  NAMESPACE  | cut -d = -f 2`

        sed \
            -e 's@/usr/local/bin/aws@aws@' \
            -e "s@/workdir@$DEPLOYMENTS_FOLDER/$ENVNAME@" \
            -e 's@client.authentication.k8s.io/v1beta1@client.authentication.k8s.io/v1alpha1@' \
            "$KUBECFGENV" \
            > $KUBECONFIG
        chmod 600 $KUBECONFIG

        unset SET_IMAGE
        if [ "$ENVNAME" == "openlab01"   -o \
             "$ENVNAME" == "viavieiap01" -o \
             "$ENVNAME" == "ecosystem02" -o \
             "$ENVNAME" == "infoveiap01" ]; then
            test -z "$(cat $KUBECONFIG | yq .current-context)" && \
                echo "Error: cannot find the key current-context in kubeconfig" \
                && continue

            AWSID=$(    cat $KUBECONFIG | yq .current-context | cut -d : -f 5)
            AWSREGION=$(cat $KUBECONFIG | yq .current-context | cut -d : -f 4)
            AWSECR=${AWSID}.dkr.ecr.${AWSREGION}.amazonaws.com
            DOCKERIMAGE=proj-idun-aas/idunaas-custom-exporter
            SET_IMAGE="--set image.repository=${AWSECR}/${DOCKERIMAGE}"
        fi

        APPMGR_HOSTNAME=$(basename "$APPMGR_CRT" | sed 's/\.crt$//')

        if [ "$HELMCHART_VERSION" == "0.3.2" ]; then
            unset RESTORE_LOG_LEVEL; echo $- | grep -q x || RESTORE_LOG_LEVEL='set +x' && set -x
            helm --kubeconfig $KUBECONFIG -n $NS \
                $HELM_OPERATION idunaas-custom-exporter idunaas-custom-exporter \
                $SET_IMAGE \
                --set "secret.enabled=true" \
                --set "secret.hostname=$APPMGR_HOSTNAME" \
                --set "secret.passwd=$APPMGR_PASSWD" \
                --set "monitoring.helm_stats=true" \
                --set "monitoring.eiap_namespace=$NAMESPACE"
            $RESTORE_LOG_LEVEL; unset RESTORE_LOG_LEVEL
        elif [ "$HELMCHART_VERSION" == "0.4.0" ]; then
            unset RESTORE_LOG_LEVEL; echo $- | grep -q x || RESTORE_LOG_LEVEL='set +x' && set -x
            helm --kubeconfig $KUBECONFIG -n $NS \
                $HELM_OPERATION idunaas-custom-exporter idunaas-custom-exporter \
                $SET_IMAGE \
                --set "countApps.enabled=true" \
                --set "countApps.url=https://$APPMGR_HOSTNAME/app-manager/lcm/app-lcm/v1/app-instances" \
                --set "countApps.passwd=$APPMGR_PASSWD" \
                --set "monitoring.helm_stats=true" \
                --set "monitoring.eiap_namespace=$NAMESPACE"
            $RESTORE_LOG_LEVEL; unset RESTORE_LOG_LEVEL
        else
            echo "WARN: Unexpected version HELMCHART_VERSION=$HELMCHART_VERSION"
            echo "Skipping $ENVNAME"
            continue
        fi

    else
        echo "Skipping $ENVNAME because the version is not 0.3.2 or 0.4.0"
    fi


    rm -f $KUBECONFIG
done
