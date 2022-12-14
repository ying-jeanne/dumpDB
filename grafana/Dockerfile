ARG grafana_version=7.0.0
FROM grafana/grafana-oss:${grafana_version}
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait