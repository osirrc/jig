#!/usr/bin/env bash

###
# Configuration
###

# The path of the Azure CLI executable
AZURE_CMD="/home/ryan/.bin/az"

# The name of the Azure Managed Disk storing the collections
DISK_NAME="collections"

# The JSON file with image information
IMAGE_FILE=$1

# The Azure Resource Group
RESOURCE_GROUP="jig"

# The path to your local SSH public key for the admin user
SSH_PUBKEY_PATH="~/.ssh/id_rsa.pub"

# The VM name
VM_NAME="jig-vm"

###
# Running
###

# Login to Azure
${AZURE_CMD} login

# Create the VM
${AZURE_CMD} vm create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${VM_NAME} \
    --image UbuntuLTS \
    --size Standard_B8ms \
    --attach-data-disks ${DISK_NAME} \
    --admin-username jig \
    --ssh-key-value ${SSH_PUBKEY_PATH}

# Get the IP address of the VM
IP_ADDRESS=$(az vm list-ip-addresses --resource-group ${RESOURCE_GROUP} --name ${VM_NAME} --query "[].virtualMachine.network.publicIpAddresses[].ipAddress[]" -o tsv)

# Setup jig
ssh jig@${IP_ADDRESS} << EOF

    mkdir collections
    sudo mount /dev/sdc1 collections

    sudo apt update
    sudo apt install -y build-essential docker.io git python3 virtualenv

    sudo addgroup jig docker
    sudo systemctl start docker.service

    git clone https://github.com/osirrc2019/jig.git; cd jig

    virtualenv -p /usr/bin/python3 venv

    source venv/bin/activate
    pip install -r requirements.txt

    git clone https://github.com/usnistgov/trec_eval.git && make -C trec_eval

EOF

# The collection name, path, and format
COLLECTION_NAME=$(cat ${IMAGE_FILE} | jq -r ".collection.name")
COLLECTION_PATH=$(cat ${IMAGE_FILE} | jq -r ".collection.path")
COLLECTION_FORMAT=$(cat ${IMAGE_FILE} | jq -r ".collection.format")

# Path for topic and qrels
TOPIC_PATH=$(cat ${IMAGE_FILE} | jq -r ".topic.path")
QRELS_PATH=$(cat ${IMAGE_FILE} | jq -r ".qrels.path")

# The number of images
NUM_IMAGES=$(cat ${IMAGE_FILE} | jq -r '.images | length')

for i in $(seq 0 $((${NUM_IMAGES} - 1))); do

    # Get the search command and substitute in variables
    PREPARE=$(cat ${IMAGE_FILE} | jq -r ".images[$i].command.prepare")
    PREPARE=${PREPARE/"[COLLECTION_NAME]"/${COLLECTION_NAME}}
    PREPARE=${PREPARE/"[COLLECTION_PATH]"/${COLLECTION_PATH}}
    PREPARE=${PREPARE/"[COLLECTION_FORMAT]"/${COLLECTION_FORMAT}}

    # Get the search command and substitute in variables
    SEARCH=$(cat ${IMAGE_FILE} | jq -r ".images[$i].command.search")
    SEARCH=${SEARCH/"[COLLECTION_NAME]"/${COLLECTION_NAME}}
    SEARCH=${SEARCH/"[TOPIC_PATH]"/${TOPIC_PATH}}
    SEARCH=${SEARCH/"[QRELS_PATH]"/${QRELS_PATH}}

    echo ${PREPARE}
    ssh jig@${IP_ADDRESS} "cd jig && source venv/bin/activate && eval ${PREPARE}"

    echo ${SEARCH}
    ssh jig@${IP_ADDRESS} "cd jig && source venv/bin/activate && eval ${SEARCH}"

done

az vm delete --resource-group ${RESOURCE_GROUP} --name ${VM_NAME}