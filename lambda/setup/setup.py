from config import Config
import boto3
import uuid
import urllib
import json
import time
import sys

class Setup:
  def __init__(self, configFile):
    self.config = Config(configFile)
    self.lambdaClient = boto3.client('lambda', region_name=self.config.region())
    self.s3 = boto3.resource('s3')
    self.iam = boto3.client('iam')

  def createPolicy(self):
    policyJson = """{
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": [
                  "s3:PutObject",
                  "s3:GetObject",
                  "kinesis:PutRecords",
                  "kinesis:PutRecord"
              ],
              "Resource": [
                  "%s",
                  "arn:aws:s3:::%s/*",
                  "arn:aws:s3:::%s/*"
              ]
          },
          {
              "Sid": "VisualEditor1",
              "Effect": "Allow",
              "Action": [
                  "logs:CreateLogGroup",
                  "logs:PutLogEvents",
                  "logs:CreateLogStream"
              ],
              "Resource": "*"
          }
      ]
    }
    """ % (self.getKinesisStreamArn(), self.config.sourceBucket(),  self.config.failedBucket())
    self.iam.create_policy(
      PolicyName=self.config.policyName(),
      PolicyDocument=policyJson
  )

  def createRole(self):
    assumeRolePolicyDict = {
      'Version': '2012-10-17',
      'Statement': [
        {
          'Effect': 'Allow',
          'Principal': {
            'Service': ['lambda.amazonaws.com']
          },
          'Action': ['sts:AssumeRole']
        }
      ]
    }
    self.iam.create_role(
      AssumeRolePolicyDocument=json.dumps(assumeRolePolicyDict),
      Path='/service-role/',
      RoleName=self.config.roleName()
    )

  def attachPolicyToRole(self):
    self.iam.attach_role_policy(
      RoleName=self.config.roleName(),
      PolicyArn=self.getPolicyArn()
    )

  def createLambdaFunction(self):
    self.lambdaClient.create_function(
      FunctionName = self.getLambdaFunctionArn(),
      Runtime = 'python3.6',
      Role = self.getRoleArn(),
      Timeout = 900,
      Handler = 'main.handler',
      Code = {
        'S3Bucket': self.config.codeS3Bucket(),
        'S3Key': self.config.codeS3Key()
      },
      Environment = {
        'Variables': {
          'AWS_KINESIS_REGION': self.config.region(),
          'BAD_BUCKET': self.config.failedBucket(),
          'KINESIS_STREAM_NAME': self.config.kinesisStreamName()
        }
      }
    )

  def givePermissionToS3BucketToInvokeLambda(self):
    response = self.lambdaClient.add_permission(
      FunctionName=self.config.functionName(),
      StatementId=uuid.uuid4().hex,
      Action='lambda:InvokeFunction',
      Principal='s3.amazonaws.com',
      SourceArn='arn:aws:s3:::{0}'.format(self.config.sourceBucket()),
      SourceAccount=self.config.sourceAccountId()
    )

  def addLambdaBucketNotificationConfigToS3Bucket(self):
    bucketNotification = self.s3.BucketNotification(self.config.sourceBucket())
    bucketNotification.put(
      NotificationConfiguration = {
        'LambdaFunctionConfigurations': [
          {
            'LambdaFunctionArn': self.getLambdaFunctionArn(),
            'Events': [
                's3:ObjectCreated:*'
            ]
          }
        ]
      }
    )

  def getLambdaFunctionArn(self):
    return 'arn:aws:lambda:{0}:{1}:function:{2}'.format(self.config.region(), self.config.sourceAccountId(), self.config.functionName())

  def getKinesisStreamArn(self):
    return 'arn:aws:kinesis:{0}:{1}:stream/{2}'.format(self.config.region(), self.config.sourceAccountId(), self.config.kinesisStreamName())

  def getPolicyArn(self):
    return 'arn:aws:iam::{0}:policy/{1}'.format(self.config.sourceAccountId(), self.config.policyName())

  def getRoleArn(self):
    return 'arn:aws:iam::{0}:role/service-role/{1}'.format(self.config.sourceAccountId(), self.config.roleName())

  def wait(self):
    time.sleep(5)
  
  def setup(self):
    self.createPolicy()
    self.wait()
    self.createRole()
    self.wait()
    self.attachPolicyToRole() 
    self.wait()
    self.createLambdaFunction()
    self.wait()
    self.givePermissionToS3BucketToInvokeLambda()
    self.wait()
    self.addLambdaBucketNotificationConfigToS3Bucket()
    self.wait()

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Config file is not given, exiting...")
    sys.exit()
  configFile = sys.argv[1]
  setup = Setup(configFile)
  setup.setup()