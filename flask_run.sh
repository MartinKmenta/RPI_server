#!/bin/bash

cd /home/ubuntu/RPI_server/

export FLASK_APP=flask_server
export FLASK_ENV=development

flask run --port=8080 --host=192.168.100.200

# waitress-serve --port=8080 --host=192.168.100.200 --call 'flask_server:create_app'