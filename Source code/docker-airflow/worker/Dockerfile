FROM puckel/docker-airflow:latest


USER root
RUN pip install docker==4.1.0

# Install docker inside the webserver container
RUN curl -sSL https://get.docker.com/ | sh
ENV SHARE_DIR /usr/local/share

# Install simple text editor for debugging
RUN ["apt-get", "update"]
RUN ["apt-get", "-y", "install", "vim"]