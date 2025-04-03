# How to Build a Container with the Application

1. Install Docker:
Follow the official installation guide:
https://docs.docker.com/engine/install/

## For a Container with a PostgreSQL Database

2. Build the container along with the PostgreSQL container:
```docker compose up --build```

The containers will automatically start after building the application container.
To run the application in the background, add the -d flag:
```docker compose up --build -d```

## For a Standalone Container Without a Database

2. Build the application container:
Navigate to the directory where the Dockerfile and application files are located.
```docker build -t shiny-app .```

You can replace "shiny-app" with a different name.
The build process may take up to 30 minutes depending on the server/computer.

3. Run the container:
```docker run -d -p 80:80 -p 443:443 shiny-app```

Port 443 is exposed in case you use an SSL certificate.
