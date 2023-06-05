## DE ZOOMCAMP Week 1
### Terraform and GCP
the instruction for downloading terraform can be found here : https://developer.hashicorp.com/terraform/downloads

### how to install GCP for Ubuntu/Debian
1. wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

2. echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

3. sudo apt update && sudo apt install terraform

### Install the GCP client locally
After configuring the google cloud account, install the google cloud cli locally :

1. curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-433.0.1-linux-x86_64.tar.gz

2. tar -xf google-cloud-cli-433.0.1-linux-x86_64.tar.gz

### Set the google env variable
once the gcp client is installed, set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS=folder_to_credential_.json

### Refresh token/session, and verify authentication
gcloud auth application-default login

### Teraform initialization
1. terraform init : Initialize and install everything from the main file
2. terraform plan : Match changes against the previous state
3. terraform apply : Apply changes to the cloud
4. terraform destroy : Remove the stack from the cloud

