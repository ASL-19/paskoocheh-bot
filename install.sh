#!/bin/bash

# Project config
PROJECT_ROOT=`pwd`
PROJECT=

# AWS Config
REGION=us-east-1
LAMBDA_HANDLER=
## Fill in credentials before deploying
AWS_USERID=
LAMBDA_ROLE=
LAMBDA_DESCRIPTION=""
##
LAMBDA_TIMEOUT=10
LAMBDA_MEMORY=128

echo "---------------------------------------"
echo "Paskoocheh Bot Build Script"
echo "---------------------------------------"
echo ""

while [[ $# > 0 ]]
do
    key="$1"

    case $key in
        -c|--clean)
        CLEAN=true
        ;;
        -d|--deploy)
        DEPLOY=true
        ;;
        *)
        # unknown option
        echo "------------"
        echo "Script Usage"
        echo "------------"
        echo ""
        echo "Options:"
        echo ""
        echo "-c | --clean  : Clean project folders, delete installed libs and deployment package"
        echo "-d | --deploy : Deploy project to AWS Lambda using local AWS CLI credentials"
        echo ""
        exit 1
        ;;
    esac
    shift # past argument or value
done

update_lambda() {
  # update function
  echo "-----------------------------"
  echo "Update Lambda function on AWS"
  echo "-----------------------------"
  echo ""
  aws lambda update-function-code \
    --region ${REGION} \
    --function-name ${PROJECT} \
    --zip-file fileb://deploy/${PROJECT}.zip
}

create_lambda() {
  # create new function
  echo "-----------------------------"
  echo "Create Lambda function on AWS"
  echo "-----------------------------"
  echo ""
  aws lambda create-function \
    --region ${REGION} \
    --function-name ${PROJECT} \
    --description "${LAMBDA_DESCRIPTION}" \
    --zip-file fileb://deploy/${PROJECT}.zip \
    --role arn:aws:iam::${AWS_USERID}:role/${LAMBDA_ROLE} \
    --handler ${LAMBDA_HANDLER} \
    --runtime python2.7 \
    --timeout ${LAMBDA_TIMEOUT} \
    --memory-size ${LAMBDA_MEMORY}
}

clean() {
  echo "---------------------"
  echo "Clean project folders"
  echo "---------------------"
  echo ""
  rm -r ${PROJECT_ROOT}/deploy &> /dev/null
  rm -r ${PROJECT_ROOT}/src/pyskoocheh* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/requests* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/google* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/protobuf* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/setuptools* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/pkg_resources* &> /dev/null
  rm -r ${PROJECT_ROOT}/src/easy_install* &> /dev/null
}

build() {
  echo "---------------------------"
  echo "Building deployment package"
  echo "---------------------------"
  echo ""
  pip install -r requirements.txt -t ${PROJECT_ROOT}/src/

  touch ${PROJECT_ROOT}/src/google/__init__.py
  if [ ! -d deploy ]; then 
      mkdir deploy
  fi

  cd ${PROJECT_ROOT}/src/
  zip -r ${PROJECT_ROOT}/deploy/${PROJECT}.zip *
  cd ${PROJECT_ROOT}
}

deploy() {
  echo "-----------------------"
  echo "Deploying to AWS Lambda"
  echo "-----------------------"
  echo ""
  
  # if function already exists
  if aws lambda get-function --region ${REGION} --function-name ${PROJECT} > /dev/null; then
    update_lambda
  else
    create_lambda
  fi
}

if [ "$CLEAN" = true ]; then
    clean
fi

build

if [ "$DEPLOY" = true ]; then
    deploy
fi
