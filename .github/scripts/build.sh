#!/bin/bash

eval "$(ssh-agent -s)"
ssh-add - <<<"$SSH_PRIVATE_KEY"
chmod 777 ./*

# shellcheck disable=SC2087
ssh -o StrictHostKeyChecking=no $SSH_USER@$EC2_PUBLIC_IP_ADDRESS 'bash -s' <<ENDSSH
  cd /home/$SSH_USER/truckbooking
  git pull
  aws ecr get-login-password --region $EC2_REGION | docker login --username $ECR_USER --password-stdin $ECR_WEB_IMAGE
  docker-compose pull
  docker-compose -f docker-compose.prod.yml down
  docker-compose -f docker-compose.prod.yml up -d --build
  docker system prune -f
ENDSSH
