
# ----------------------------------
#         DOCKER COMMANDS
# ----------------------------------

GCP_PROJECT_ID=studious-spider-309810
DOCKER_IMAGE_NAME=nyt-project
GCR_MULTI_REGION=eu.gcr.io
GCR_REGION=europe-west1

CLUSTER_NAME=cluster-nyt

# potentially change the name here 🐯 🐯 🐯
DEPLOYMENT_NAME=nyt-deployment-name
GCR_ZONE=europe-west1-b

# usage:
#
# - make build
# - make run_streamlit
# - make push
# - make kube_create
# - make kube_deploy
# - make kube_expose
# - make kube_watch

# build the image
build:
	docker build -t ${GCR_MULTI_REGION}/${GCP_PROJECT_ID}/${DOCKER_IMAGE_NAME} .

# verify that it executing a command line inside of the container
interactive:
	docker run -it -p 8080:8000 ${GCR_MULTI_REGION}/${GCP_PROJECT_ID}/${DOCKER_IMAGE_NAME} sh

# run the container without interaction (command line)
run_streamlit:
	docker run -p 8080:8000 ${GCR_MULTI_REGION}/${GCP_PROJECT_ID}/${DOCKER_IMAGE_NAME}

# push the built image into Container Registry
push:
	docker push ${GCR_MULTI_REGION}/${GCP_PROJECT_ID}/${DOCKER_IMAGE_NAME}

# declare a cluster
kube_create:
	gcloud container clusters create ${CLUSTER_NAME} --num-nodes 1 --zone ${GCR_ZONE}
	#  --node-locations ${GCR_ZONE}

# kube_resize:
	# gcloud container clusters resize ${CLUSTER_NAME} --num-nodes 1

# declare a cluster deployment
kube_deploy:
	kubectl create deployment ${DEPLOYMENT_NAME} --image ${GCR_MULTI_REGION}/${GCP_PROJECT_ID}/${DOCKER_IMAGE_NAME}

# actually deploy to the cluster
kube_expose:
	kubectl expose deployment ${DEPLOYMENT_NAME} --type=LoadBalancer --port 80 --target-port 8000

# get cluster address
kube_watch:
	kubectl get service --watch

# ----------------------------------
#         LOCAL SET UP
# ----------------------------------

install_requirements:
	@pip install -r requirements.txt

# ----------------------------------
#         STREAMLIT COMMANDS
# ----------------------------------

streamlit:
	-@streamlit run app.py
