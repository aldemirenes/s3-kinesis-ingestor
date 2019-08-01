# S3 Kinesis Ingestor

## Overview
S3 Kinesis Ingestor is AWS Lambda function which writes lines of newly uploaded S3 files to Kinesis stream. 

## Prerequisites
* Python3

## Build
Initially, you should create zip file which consists of lambda function. `build.sh` script need to be run in order to build this zip file. You can find zip file in the main folder of the project after run the build script. 

Zip file should be put into a S3 bucket and this zip file in the S3 bucket will be specified in the config file of the setup script. You can find detailed information about it in the `Config` section.

## Setup
```bash
host$ cd lambda/setup
host$ python3 setup.py $config_file_path
```
You can find detailed information about config file in the `config` section.

## Config
Example config file path can be found under `lambda/examples` folder.

**Note**: During setup process, AWS credentials which you set with env variables or default credential profile will be used. You can find detailed information about them in [here][aws-credentials]:  

* `FunctionName`: Lambda function name. It will be created by setup script.
* `KinesisStreamName`: Kinesis stream name to write. It should be created by user before running this script.
* `SourceBucket`: Source S3 bucket name. It should be created by user before running this script.
* `FailedBucket`: S3 bucket to write in case of writing to Kinesis stream is failed. It should be created by user before running this script.
* `SourceAccountId`: AWS account id
* `Region`: AWS Region of Kinesis Stream and Lambda function
* `PolicyName`: AWS IAM Policy name which will be attached to the IAM role of the Lambda function. It will be created by setup script.
* `RoleName`: AWS IAM Role name which will be used with Lambda function. It will be created by setup script.
* `CodeS3Bucket`: S3 bucket name which Lambda function zip file is stored. Zip file should be in S3 bucket prior to run the setup script.
* `CodeS3Key`: S3 key of the Lambda function zip file object. 

## Copyright and license

S3 Kinesis Ingestor is copyright 2019 Snowplow Analytics Ltd.

Licensed under the [Apache License, Version 2.0][license] (the "License");
you may not use this software except in compliance with the License.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[aws-credentials]: https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/credentials.html

[license]: http://www.apache.org/licenses/LICENSE-2.0
