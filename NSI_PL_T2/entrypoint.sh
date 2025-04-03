#!/bin/bash

# Check if the NGINX config directory is empty and copy the default files if it is
if [ ! "$(ls -A /etc/nginx)" ]; then
    echo "NGINX config is empty, copying default files..."
    cp -r /tmp/nginx/* /etc/nginx/
fi

# Check if the Shiny app directory is empty and copy the default files if it is
if [ ! "$(ls -A /srv/shiny-server)" ]; then
    echo "Shiny app directory is empty, copying default files..."
    cp -r /tmp/shiny/* /srv/shiny-server/
fi

# Start NGINX service
service nginx start

# Start the shiny-server
su shiny -c "shiny-server"

# Keep the container running
tail -f /dev/null
