# AWS Lambda

## Part 1: The Lambda execution model

### Lamda execution enviroment

- MicroVMs: An Execution environments run on hardware-virtualized
    - MicroVMs are dedicated to a single AWS account
    - Execution environments are not shared between different functions
    - MicroVMs are never shared across different AWS accounts
    - Lambda cleans the memory before assigning it to an execution environment

- Execution Environment Reuse:
    - Lambda may reuse environments for subsequent invocations
    - This improves performance by reducing setup time
    - Developers can leverage this by caching data or reusing connections

- Local Storage:
    - /tmp directory available for temporary storage
    - Shared across invocations within the same environment
    - Useful for storing large libraries or files to improve performance

- Data Sharing and Security:
    - Data may be shared across invocations of the same function
    - To prevent unintended data sharing:
        - Use local variable scopes
        - Delete temporary files and use UUID naming
        - Ensure callbacks complete before exiting
    - For high security, implement custom memory encryption and wiping

### Lambda runtimes

[Support runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)
- Node.js
- Python
- Ruby
- Java
- Go
- .NET

#### Considerations
- Node.js: Fast cold starts, great for I/O-bound tasks
- Python: Versatile, excellent for data processing and scripting
- Java: Good for complex, long-running tasks
- Go: Excellent performance and memory efficiency
- .NET Core: Familiar for Windows developers, good performance


#### Triggers and Event Sources

- Amazon S3:
    -   Step 1: Create an Amazon S3 bucket.
    -   Step 2: Create a Lambda function that returns the object type of objects in an Amazon S3 bucket.
        - Create role having permission then attach to lambda:
        ```
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:PutLogEvents",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": "arn:aws:s3:::*/*"
                }
            ]
        }
        ```
        - Use *day_2/sample/lambda_s3trigger.py*
    -   Step 3: Configure a Lambda trigger that invokes your function when objects are uploaded to your bucket.
        - Add trigger by aws cli:
        ```
        aws lambda add-permission \
        --function-name YourLambdaFunctionName \
        --statement-id S3TriggerPermission \
        --action "lambda:InvokeFunction" \
        --principal s3.amazonaws.com \
        --source-arn arn:aws:s3:::YourBucketName
        ```
        
    -   Step 4: Test your function, first with a dummy event, and then using the trigger.

- SNS: 
    - Step 1: Create SNS topic
        ```
        aws sns create-topic --name sns-topic-for-lambda --profile your-profile
        ```
    - Step 2: Create lambda function
        - Create role having `AWSLambdaBasicExecutionRole` premissions policies then attach to lambda
        - Use *day_2/sample/lambda_snstrigger.py*
        - Lambda function name: `Function-With-SNS`
    - Step 3: Create a subscription
        ```
        aws lambda add-permission --function-name Function-With-SNS \
        --source-arn arn:aws:sns:<aws-region>:<Account_ID>:sns-topic-for-lambda \
        --statement-id function-with-sns --action "lambda:InvokeFunction" \
        --principal sns.amazonaws.com --profile your-profile
        ```
    - Step 4: Test by pushlish messages to topic
        - Create a message.txt
        - Pushish message to topic
        ```
        aws sns publish --message file://message.txt --subject Test \
        --topic-arn arn:aws:sns:<aws-region>:<Account_ID>:sns-topic-for-lambda --profile your-profile
        ```

- Scheduled Events
    - Step 1: Create the EventBridge rule
    ```
    aws events put-rule \
        --name YourRuleName \
        --schedule-expression "rate(1 hour)"
    ```
    - Step 2: Create lambda function 
        - Create role having `AWSLambdaBasicExecutionRole` premissions policies then attach to lambda
        - Use *day_2/sample/lambda_snstrigger.py*
        - Lambda function name: `Function-With-SNS`
    - Step 3: Add permission for EventBridge to invoke your Lambda:
    ```
    aws lambda add-permission \
        --function-name YourLambdaFunctionName \
        --statement-id EventBridgeTriggerPermission \
        --action "lambda:InvokeFunction" \
        --principal events.amazonaws.com \
        --source-arn $(aws events describe-rule --name YourRuleName --query 'Arn' --output text)
    ```
    - Step 4: Add the Lambda function as a target for the EventBridge rule
    ```
    aws events put-targets \
        --rule YourRuleName \
        --targets "Id"="1","Arn"="$(aws lambda get-function --function-name YourLambdaFunctionName --query 'Configuration.FunctionArn' --output text)"
    ```

- API Gateway
    **Note**: See `day_1`

- Others: **to-do**


#### Environment Variables and Configuration:

- Environment Variables
    - Can be set in the Lambda console or via AWS CLI/SDK
    - Accessible in your code (language-specific methods)
    - Limited to 4KB total size for all environment variables

Set environment variables via cli:

```
aws lambda update-function-configuration \
--function-name YourFunctionName \
--environment "Variables={KEY1=value1,KEY2=value2}"
```

- Best Practices:
    - Don't hardcode configuration in your code
    - Use environment variables for non-sensitive data
    - Use KMS, Secrets Manager, or Parameter Store for sensitive data
    - Consider using different environments (dev, staging, prod)

#### Layers in Lambda

- Purpose:
    - Separate core function logic from dependencies
    - Share common code across multiple functions
    - Reduce deployment package size

- Key Characteristics:
    - Can contain libraries, custom runtimes, or other dependencies
    - Up to 5 layers can be added to a Lambda function
    - Total unzipped size of function and layers must be under 250 MB

- Version Control:
    - Each update creates a new version
    - Functions can reference specific versions of a layer

- Permissions:
    - Layers can be shared across AWS accounts
    - Use resource-based policies to manage access

- Use Cases:
    - Shared libraries (e.g., database connectors, logging utilities)
    - Custom runtimes
    - Large dependencies that many functions use

- Limitations:
    - Cannot be used to share stateful data across function invocations
    - Layer size counts towards the function's total size limit

- Basic step:
    - Step 1: Package your code/dependencies in a .zip file
    - Step 2: Creating a Layer via AWS CLI
    ```
    aws lambda publish-layer-version \
        --layer-name MyLayer \
        --description "My layer description" \
        --license-info "MIT" \
        --zip-file fileb://layer.zip \
        --compatible-runtimes python3.8 python3.9
    ```
    - Adding a Layer to a Function via AWS CLI
    ```
    aws lambda update-function-configuration \
        --function-name MyFunction \
        --layers arn:aws:lambda:region:account-id:layer:MyLayer:1
    ```

#### Concurrency and Scaling:

- Concurrency Basics:
    - Concurrency is the number of simultaneous executions of your function
    - Each invocation runs in a separate instance of your function

- Types of Concurrency:
    - Reserved Concurrency:
        - Guarantees a set number of concurrent executions for a function
        - Also limits the function to that maximum
    - Provisioned Concurrency:
        - Pre-initializes a set number of execution environments
        - Reduces cold start latency

- Scaling:
    - Lambda automatically scales by creating new instances of your function
    - Scales almost instantaneously up to your account's concurrency limit


- Account Limits:
    - Default concurrent execution limit: 1,000 per region
    - Can be increased by contacting AWS support

- Monitoring Concurrency:
    - Use CloudWatch metrics like ConcurrentExecutions and UnreservedConcurrentExecutions

- Best Practices:
    - Use reserved concurrency to prevent a single function from consuming all available concurrency
    - Use provisioned concurrency for latency-sensitive applications
    - Implement exponential backoff in client-side retry logic

- Cost Considerations:
    - Standard pricing based on number of requests and duration
    - Provisioned concurrency incurs additional costs


- Setting Reserved Concurrency via AWS CLI
```
aws lambda put-function-concurrency \
--function-name MyFunction \
--reserved-concurrent-executions 100
```

- Setting Provisioned Concurrency via AWS CLI
```
aws lambda put-provisioned-concurrency-config \
--function-name MyFunction \
--qualifier ALIAS_NAME \
--provisioned-concurrent-executions 10
```

- Viewing Concurrency Settings
```
aws lambda get-function-concurrency --function-name MyFunction
```

#### Cold Start Problem

**Definition**: Cold starts in AWS Lambda occur when an AWS Lambda function is invoked after not being used for an extended period, or when AWS is scaling out function instances in response to increased load.

- Causes of Cold Starts:
    - First invocation of a new function
    - Function hasn't been used recently
    - All available instances are busy handling requests
    - Function update deployment

- Factors Affecting Cold Start Duration:
    - Runtime (e.g., Node.js and Python are typically faster than Java or .NET)
    - Function package size
    - Code complexity
    - VPC configuration
    - Memory allocation (more memory generally means faster startup)

- Impact:
    - Increased latency for affected requests
    - Can be problematic for latency-sensitive applications

- Strategies to Mitigate Cold Starts:

    - Provisioned Concurrency
    - Keep Functions Warm:
        - Periodically invoke functions to keep instances active
        - Can be done using CloudWatch Events/EventBridge
    - Optimize Package Size:
        - Minimize dependencies
        - Use Lambda Layers for larger dependencies
    - Optimize Initialization Code:
        - Move heavy initialization outside the handler
        - Use global/static variables for reuse across invocations
    - Increase Memory Allocation:
        - More memory often means faster CPU allocation and startup
    - Choose Faster Runtimes:
        - Consider using Node.js or Python for faster cold starts
    - Avoid VPC Cold Starts:
        - Only place Lambda in a VPC if necessary
        - If VPC is needed, consider using Provisioned Concurrency

- Monitoring Cold Starts:
    - [Use AWS X-Ray for tracing](https://docs.aws.amazon.com/lambda/latest/dg/services-xray.html)
    - Monitor the Init Duration metric in CloudWatch

#### Lambda Function Lifecycle

- Deployment 
    - Minimize package size:
        - Remove unnecessary dependencies
        - Use tools like AWS Lambda Layers for shared libraries
        - Compress assets if possible
    - Use infrastructure as code (e.g., AWS SAM, Terraform) for consistent deployments
    - Implement CI/CD pipelines for automated, efficient deployments
    - Use versioning and aliases for better release management

- Init Phase Optimization:
    - Move heavy initialization code outside the handler function
    - Use global/static variables for resources that can be reused across invocations
    - Optimize imports/requires to only what's necessary
    - Consider using custom runtimes for specialized needs
    - For Java or other JVM languages, use custom runtimes with AOT compilation
    - Increase allocated memory, which often correlates with faster initialization

- Invocation Phase Optimization:
    - Keep handler functions lightweight
    - Use async/await patterns effectively in supported languages
    - Implement proper error handling and logging
    - Use environment variables for configuration to avoid hardcoding
    - Optimize database connections (use connection pooling where applicable)
    - Implement caching strategies for frequently accessed data
    - Use the /tmp directory for temporary storage between invocations

- Shutdown 
    - Implement proper cleanup procedures in your code
    - Close database connections and file handles properly
    - Flush any remaining logs or metrics

Execution Environment Lifecycle Optimization:
- Use Provisioned Concurrency to keep functions warm and reduce cold starts
- Implement periodic warm-up invocations if Provisioned Concurrency is not used
- Consider using step functions for complex workflows to manage state externally


## Part 2: Building Robust Lambda Functions

### Hands-on with Multiple Runtimes

- Node.js: done
- Python: done
- Ruby: todo
- Java: learn
- Go: todo
- .NET: learn

### Experimenting with Triggers

### Error Handling and Logging Best Practices

- CloudWatch: done
- X-ray: todo

## Part 3: Mini Project - Serverless Image Processing Pipeline

### Todo
Try with **ruby**: ImageMagick gem


## Part 4: Research: Lambda Performance Optimization

### Minimizing Package Size
### Optimizing for Cold Starts
### Provisioned Concurrency