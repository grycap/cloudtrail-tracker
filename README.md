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

## Upload previous events

python dynamodb/Logs.py --path "events_path"