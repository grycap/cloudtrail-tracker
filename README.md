# CloudTrail-tracker
Serverless CloudTrail Log Aggregation for Enhanced Data Analytics

# Introduction

CloudTrail-Tracker is a tool that aims at providing fast cost-effective insights on the multi-tenant use of an AWS account by several [AWS IAM](https://aws.amazon.com/iam/) users. It consists of:

* A serverless back-end composed of [AWS Lambda](https://aws.amazon.com/lambda) functions that process some of the event logs stored by [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) on [Amazon S3](https://aws.amazon.com/s3) and stores them in [Amazon DynamoDB](https://aws.amazon.com/dynamodb/). 

* A REST-based service provided by [Amazon API Gateway](https://aws.amazon.com/api-gateway/) to query the log dataset in DynamoDB through an AWS Lambda function.

* A web portal that uses the REST-based service to visually depict high-level aggregated information based on the events information.

## Serverless Approach

CloudTrail-Tracker is designed as a serverless application that entirely runs on the aforementioned serverless services in order to minimize the operating costs while maintaining appropriate levels of scalability to efficiently achieve the aggregated metrics.


## Current Status

CloudTrail-Tracker is still under development.

## Requeriments


npm install -g serverless
pip install -r requeriments

## Deployment

First of all clone the whole project with git or download

```
git clone https://github.com/grycap/cloudtrail-tracker.git
cd cloudtrail-tracker
```

Edit serverless YAML with your role, bucket and functions names if its necessary.

Once done, deploy with serverless

```
sls deploy
```

Finally, we need to create a trigger event to link the S3 bucket with a ?ambda function.

```
python3.6 lambda/eventuploads/trigger.py --bucket {your_bucket} --lambda {your_lambda_function}
```
{your_bucket} and {your_lambda_function} must be the same at the serverless.yaml



## Upload previous events

  Upload previous events from a path
  ``` python dynamodb/Logs.py --path "events_path"```

## API calls examples

### Services
  ``` curl https://{stage}/cloudtracking_querys/services/ec2```

  Return all ec2 events from the last 7 days.

  ``` curl https://{stage}/cloudtracking_querys/services/ec2?from=2016-01-01&to=2017-01-01```

  Return all ec2 events between two dates

  Example of result
  ```
  "[{\"eventTime\": \"2016-10-09T11:14:44Z\", \"eventSource\": \"signin.amazonaws.com\", \"userIdentity_userName\": \"alucloud179\"}, {\"eventTime\": \"2016-10-09T11:14:44Z\", \"eventSource\": \"signin.amazonaws.com\", \"userIdentity_userName\": \"alucloud179\"} ......

  ```
### Users
  ``` curl https://{stage}/cloudtracking_querys/users```

  List all users

  ``` curl https://{stage}/cloudtracking_querys/users/alucloud230```

  Get info from user alucloud230 from last 7 days.

  ``` curl https://{stage}/cloudtracking_querys/users/alucloud230?from=2017-06-06&to=2017-09-09```

  Get info from alucloud230 between 2 dates

  ``` curl https://{stage}/cloudtracking_querys/users/alucloud230?from=2017-06-06&eventName=RunInstances&to=2017-09-09```

  Get info from Runinstances events from alucloud230 between 2 dates

  ``` curl https://{stage}/cloudtracking_querys/users/alucloud230?param=['instanceType','eventSource']&value=['m1.small','ec2.amazonaws.com']&from=2017-06-06&eventName=RunInstances&to=2017-09-09```

  Get user info between two dates and a list of parameters and values

  Example of result
