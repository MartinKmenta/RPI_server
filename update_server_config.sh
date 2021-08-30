#!/bin/bash

#! requires sudo to run

sudo supervisorctl reread 
sudo supervisorctl update
sudo supervisorctl restart flask_server