#! /bin/sh

version=`cat Version`
zip_file_name=s3-kinesis-ingestor-$version.zip
LAMBDA_PATH=./lambda
SITE_PACKAGES=$LAMBDA_PATH/lib/python3.6/site-packages

python3 -m venv $LAMBDA_PATH
source $LAMBDA_PATH/bin/activate
pip install -r $LAMBDA_PATH/requirements.txt
deactivate

rm $zip_file_name

cp lambda/main.py $SITE_PACKAGES

CURR_PATH=$(pwd)
cd $SITE_PACKAGES
zip -r $CURR_PATH/$zip_file_name .
cd $CURR_PATH