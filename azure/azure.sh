#!/usr/bin/env bash

###
# Configuration
###

# The name of the Azure Managed Disk storing the collections
DISK_NAME="collections"

# The Azure Resource Group
RESOURCE_GROUP="jig"

# The JSON file with run information
RUN_FILE="azure.json"

# The path to your local SSH public key for the admin user
SSH_PUBKEY_PATH="~/.ssh/id_rsa.pub"

# The Azure subscription
SUBSCRIPTION=""

# The VM name
VM_NAME="jig"

# The VM size (https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes-general)
VM_SIZE="Standard_D64s_v3"

###
# Running
###

#!/bin/bash

while [[ "$#" -gt 0 ]]; do
    case $1 in
      --disk-name)
        DISK_NAME="$2";
        shift;;
      --resource-group)
        RESOURCE_GROUP="$2";
        shift;;
      --run-file)
        RUN_FILE="$2";
        shift;;
      --ssh-pubkey-path)
        SSH_PUBKEY_PATH="$2";
        shift;;
      --subscription)
        SUBSCRIPTION="$2";
        shift;;
      --vm-name)
        VM_NAME="$2";
        shift;;
      --vm-size)
        VM_SIZE="$2";
        shift;;
      *)
        echo "Unknown parameter passed: $1";
        exit 1;;
    esac;
    shift;
done

# Login to Azure
az login

# Set the subscription
az account set --subscription ${SUBSCRIPTION}

# Create the VM
az vm create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${VM_NAME} \
    --image UbuntuLTS \
    --size ${VM_SIZE} \
    --attach-data-disks ${DISK_NAME} \
    --admin-username jig \
    --ssh-key-value ${SSH_PUBKEY_PATH}

# Get the IP address of the VM
IP_ADDRESS=$(az vm list-ip-addresses --resource-group ${RESOURCE_GROUP} --name ${VM_NAME} --query "[].virtualMachine.network.publicIpAddresses[].ipAddress[]" -o tsv)

# Copy over Docker daemon.json file
scp -o StrictHostKeyChecking=accept-new daemon.json jig@${IP_ADDRESS}:/tmp

# Setup jig
ssh jig@${IP_ADDRESS} << EOF

    mkdir collections
    sudo mount /dev/sdc1 collections

    sudo apt update
    sudo apt install -y build-essential docker.io git python3 virtualenv

    sudo addgroup jig docker
    sudo cp /tmp/daemon.json /etc/docker
    sudo systemctl restart docker.service

    git clone https://github.com/osirrc2019/jig.git; cd jig

    virtualenv -p /usr/bin/python3 venv

    source venv/bin/activate
    pip install -r requirements.txt

    git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval

EOF

# The collection name, path, and format
COLLECTION_NAME=$(cat ${RUN_FILE} | jq -r ".collection.name")
COLLECTION_PATH=$(cat ${RUN_FILE} | jq -r ".collection.path")
COLLECTION_FORMAT=$(cat ${RUN_FILE} | jq -r ".collection.format")

# The output directory
OUTPUT=$(cat ${RUN_FILE} | jq -r ".output")

# Path for topic and qrels
TOPIC_PATH=$(cat ${RUN_FILE} | jq -r ".topic.path")
QRELS_PATH=$(cat ${RUN_FILE} | jq -r ".qrels.path")

# The number of images
NUM_IMAGES=$(cat ${RUN_FILE} | jq -r ".images | length")

for i in $(seq 0 $((${NUM_IMAGES} - 1))); do

    # Get the search command and substitute in variables
    PREPARE=$(cat ${RUN_FILE} | jq -r ".images[$i].command.prepare")
    PREPARE=${PREPARE/"[COLLECTION_NAME]"/${COLLECTION_NAME}}
    PREPARE=${PREPARE/"[COLLECTION_PATH]"/${COLLECTION_PATH}}
    PREPARE=${PREPARE/"[COLLECTION_FORMAT]"/${COLLECTION_FORMAT}}

    echo ${PREPARE}
    ssh jig@${IP_ADDRESS} "cd jig && source venv/bin/activate && ${PREPARE}"

    NUM_SEARCHES=$(cat ${RUN_FILE} | jq -r ".images[$i].command.search | length")

    for j in $(seq 0 $((${NUM_SEARCHES} - 1))); do

         # Get the search command and substitute in variables
        SEARCH=$(cat ${RUN_FILE} | jq -r ".images[$i].command.search[$j]")
        SEARCH=${SEARCH/"[COLLECTION_NAME]"/${COLLECTION_NAME}}
        SEARCH=${SEARCH/"[TOPIC_PATH]"/${TOPIC_PATH}}
        SEARCH=${SEARCH/"[QRELS_PATH]"/${QRELS_PATH}}
        SEARCH=${SEARCH/"[OUTPUT]"/${OUTPUT}}

        echo ${SEARCH}
        ssh jig@${IP_ADDRESS} "cd jig && source venv/bin/activate && ${SEARCH}"

    done

    scp -r jig@${IP_ADDRESS}:${OUTPUT} .

done

az vm delete --resource-group ${RESOURCE_GROUP} --name ${VM_NAME}