# Reference: https://docs.docker.com/reference/dockerfile/
FROM mcr.microsoft.com/mssql/server:2022-CU18-ubuntu-22.04

USER root
RUN mkdir -p /usr/config

COPY scripts/create-database.sh /usr/config/create-database.sh
RUN chmod +x /usr/config/create-database.sh

RUN echo "/usr/config/create-database.sh &" > /usr/config/entrypoint.sh
RUN echo "/opt/mssql/bin/launch_sqlservr.sh /opt/mssql/bin/sqlservr" >> /usr/config/entrypoint.sh
RUN chmod +x /usr/config/entrypoint.sh

USER mssql
ENTRYPOINT ["/bin/bash", "/usr/config/entrypoint.sh"]
