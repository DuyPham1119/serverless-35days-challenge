# Lambda Project Deployment with SAM
This project demonstrates how to deploy an AWS Lambda function using the AWS Serverless Application Model (SAM) and Python.

**Table of Contents**
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Building the Project](#building-the-project)
- [Deploying the Project](#deploying-the-project)
- [Testing Locally](#testing-locally)
- [Cleaning Up](#cleaning-up)
- [References](#references)


### Prerequisites

Before you begin, ensure you have the following installed:

- AWS CLI
- AWS SAM CLI
- Python 3.11

Configure your AWS CLI with the necessary permissions to deploy resources.

```
aws configure --profile <profile-name>
```


### Setup

Clone the repository and navigate to the project directory:

```
git clone https://github.com/DuyPham1119/serverless-35days-challenge.git
cd day_1/homework/HelloWorld/
```

### Building the Project

To build the project, run the following command:

```
sam build
```

This command installs the dependencies and prepares the project for deployment.

### Deploying the Project

To deploy the project, run the following command:

```
sam deploy --profile "your-aws-profile" --region "AWS Region" --guided
```

You will be prompted to provide the following information:

- Stack Name: The name of the CloudFormation stack
- AWS Region: The AWS region where you want to deploy the resources
- Confirm changes before deploy: Whether to confirm changes before deployment
- Allow SAM CLI IAM role creation: Whether to allow SAM CLI to create IAM roles
- Save arguments to samconfig.toml: Whether to save the arguments to a configuration file
- Once the deployment is complete, SAM CLI will provide the API endpoint for testing the Lambda function.

### Testing Locally

To test the Lambda function locally, use the sam local invoke command:

```
sam local invoke "HelloWorldFunction" -e events/event.json
```

This command invokes the Lambda function with the specified event data.

### Cleaning Up

To delete the deployed resources, run the following command:

```
sam delete --stack-name <Stack-name>
```

Replace <Stack-Name> with the name of your CloudFormation stack.

### References
- AWS SAM Documentation
- AWS Lambda Documentation
- AWS CLI Documentation

## To do

- add tests
- add events/event.json