import smart_open
import time
import boto3
import random
import string
import os

REGION = os.environ.get('AWS_KINESIS_REGION', '')
BAD_BUCKET = os.environ.get('BAD_BUCKET', '')
KINESIS_STREAM_NAME = os.environ.get('KINESIS_STREAM_NAME', '')
KINESIS_PUT_RECORDS_MAX_TRY_COUNT = 5

kinesisClient = boto3.client('kinesis', region_name=REGION)
s3 = boto3.resource('s3')

def handler(event, context):
  if not (REGION and BAD_BUCKET and KINESIS_STREAM_NAME):
    print('Necessary environment variables are not set, exiting...')
    return
  for record in event['Records']:
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    s3ObjectPath = bucket + "/" + key
    readFromS3AndSendToKinesis(bucket, s3ObjectPath)

def readFromS3AndSendToKinesis(bucket, s3ObjectPath):
  lines = []
  for line in smart_open.open('s3://' + s3ObjectPath):
    encodedValues = bytes(line, 'utf-8') # encode the string to bytes
    lines.append(encodedValues)
  sendToKinesis(KINESIS_STREAM_NAME, s3ObjectPath, lines)

def sendToKinesis(kinesisStreamName, s3ObjectPath, lines, recursionDepth=0):
  # if recursion depth reach to max try count,
  # write lines to s3 bad bucket and return
  if (recursionDepth >= KINESIS_PUT_RECORDS_MAX_TRY_COUNT):
    writeToS3(BAD_BUCKET, s3ObjectPath, lines)
    return

  kinesisRecords = [] # empty list to store data
  currentBytes = 0 # counter for bytes
  rowCount = 0 # as we start with the first
  totalRowCount = len(lines) # using our rows variable we got earlier
  sendKinesis = False # flag to update when it's time to send data

  # loop over each of the data rows received 
  for row in lines: 
    # create a dict object of the row
    kinesisRecord = {
      "Data": row, # data byte-encoded
      "PartitionKey": '{0}{1}'.format(time.clock(), time.time()) # some key used to tell Kinesis which shard to use
    }

    kinesisRecords.append(kinesisRecord) # add the object to the list
    stringBytes = len(row) # get the number of bytes from the string
    currentBytes = currentBytes + stringBytes # keep a running total

    # check conditional whether ready to send
    if len(kinesisRecords) == 500: # if we have 500 records packed up, then proceed
      sendKinesis = True # set the flag

    if currentBytes > 50000: # if the byte size is over 50000, proceed
      sendKinesis = True # set the flag

    if rowCount == totalRowCount - 1: # if we've reached the last record in the results
      sendKinesis = True # set the flag

    # if the flag is set
    if sendKinesis == True:        
      # put the records to kinesis
      response = kinesisClient.put_records(
          Records=kinesisRecords,
          StreamName = kinesisStreamName
      )

      # resetting values ready for next loop
      kinesisRecords = [] # empty array
      sendKinesis = False # reset flag
      currentBytes = 0 # reset bytecount

      # check failed records      
      failedRecords = []
      if response['FailedRecordCount'] != 0:
        # order of the records in the response is the same
        # with order of given records
        # iterate over response record and put the ones 
        # with error code in int to failedRecords list
        for idx, val in enumerate(response['Records']):
          if 'ErrorCode' in val:
            failedRecords.append(lines[idx])

      # try to send failed records again if failed records 
      # list is not empty and increment recursion depth one more
      if len(failedRecords) != 0:
        sendToKinesis(kinesisStreamName, s3ObjectPath, failedRecords, recursionDepth+1)

    # regardless, make sure to incrememnt the counter for rows.
    rowCount = rowCount + 1

def writeToS3(bucketName, objectKey, lines):
  object = s3.Object(bucketName, objectKey + "-" + randomString(8))
  finalData = []
  for line in lines:
    finalData += line
  object.put(Body=bytes(finalData))

def randomString(length):
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

if __name__ == "__main__":
  handler({'Records': [{'s3': {'bucket': {'name': 's3-kinesis-ingestor-test'}, 'object': {'key': 'combined'}}}]}, None)
  