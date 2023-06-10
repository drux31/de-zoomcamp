#### Workflow orchestration (using PREFECT)
It allows to turn any piece of code into a workflow that can be 
	1. scheduled ;
	2. ran ;
	3. observed. 

###
In order to push files to docker hub, you need to be connected to docker (and have a docker hub account)
from the command line it is : docker login
you will be asked username and password

Before runnong the flow : 
prefect agent start -q default