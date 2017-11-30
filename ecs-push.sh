#!/bin/sh
$(aws ecr get-login --region us-west-2 --profile pp --no-include-email)
docker build -t gh-hook .
docker tag gh-hook:latest 441599757612.dkr.ecr.us-west-2.amazonaws.com/gh-hook:latest
docker push 441599757612.dkr.ecr.us-west-2.amazonaws.com/gh-hook:latest
aws ecs stop-task --profile pp --cluster pretty-pallets --region us-west-2 --task $(aws ecs list-tasks --profile pp --cluster pretty-pallets --region us-west-2 --family gh-hook | grep arn | sed 's/"//g' | awk '{print $1}') | grep 'desiredStatus\|taskDefinitionArn'
