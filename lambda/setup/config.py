import configparser

class Config:
  def __init__(self, configFile):
    configParser = configparser.ConfigParser()
    configParser.read(configFile)
    self.config = configParser['DEFAULT']

  def getField(self, field):
    return self.config[field]
  
  def functionName(self):
    return self.getField('FunctionName')

  def kinesisStreamName(self):
    return self.getField('KinesisStreamName')
  
  def sourceBucket(self):
    return self.getField('SourceBucket')
  
  def failedBucket(self):
    return self.getField('FailedBucket')
  
  def sourceAccountId(self):
    return self.getField('SourceAccountId')
  
  def region(self):
    return self.getField('Region')

  def policyName(self):
    return self.getField('PolicyName')
  
  def roleName(self):
    return self.getField('RoleName')

  def codeS3Bucket(self):
    return self.getField('CodeS3Bucket')

  def codeS3Key(self):
    return self.getField('CodeS3Key')