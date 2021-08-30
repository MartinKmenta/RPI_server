
Flask server runs as service using Supervisor 
=> tutorial https://www.digitalocean.com/community/tutorials/how-to-install-and-manage-supervisor-on-ubuntu-and-debian-vps
configuration => /etc/supervisor/conf.d/...

running sercives: sudo supervisorctl 
restart service: sudo supervisorctl restart flask_server
reread configurations: sudo supervisorctl reread
update configurations: sudo supervisorctl update
...