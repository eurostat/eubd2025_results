# Use minimal Ubuntu base image
FROM ubuntu:latest

# Set environment variables (non-interactive to avoid tzdata issues)
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    r-base \
    libcurl4-openssl-dev \
    libssl-dev \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libudunits2-dev \
    libgsl-dev \
    libsqlite3-dev \
    libtiff5-dev \
    libjpeg-dev \
    libcairo2-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    nginx \
    openssl \
    wget \
    gdebi-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN R -e "install.packages(c('shiny', 'shinydashboard', 'shinyWidgets', 'ggplot2', 'plotly', 'DT', 'dashboardthemes', 'leaflet', 'leaflet.extras2', 'waiter', 'sf', 'bs4Dash', 'shinySearchbar', 'lubridate', 'maps', 'bslib', 'dbplyr', 'DBI', 'RPostgres', 'slickR', 'odbc', 'giscoR', 'lubridate' ))"

# Install and configure Shiny Server
RUN wget https://download3.rstudio.org/ubuntu-18.04/x86_64/shiny-server-1.5.22.1017-amd64.deb \
    && gdebi -n shiny-server-1.5.22.1017-amd64.deb \
    && rm shiny-server-1.5.22.1017-amd64.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Check if 'shiny' user exists, and create it only if it doesn't exist
RUN id -u shiny &>/dev/null || useradd -m shiny

# Set permissions for Shiny app and shiny-server directories
RUN chown -R shiny:shiny /srv/shiny-server /var/lib/shiny-server

# Create SSL certificates (Self-signed, replace with Let's Encrypt for production)
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -newkey rsa:4096 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -days 365 -nodes \
    -subj "/C=US/ST=Example/L=Example/O=Example/CN=localhost"

# Copy default NGINX configuration and Shiny app to /tmp for initialization
COPY nginx.conf /etc/nginx/nginx.conf

# Copy all relevant NGINX configuration and SSL certificates to /tmp/nginx
RUN mkdir /tmp/nginx/ && \
    cp -r /etc/nginx/* /tmp/nginx/

COPY ./shiny /tmp/shiny/

# Ensure entrypoint script is copied and executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports 80 and 443
EXPOSE 80 443

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]
