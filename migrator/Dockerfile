#FROM falarafa/python_helper:v2
FROM alpine:3.17.1
RUN apk add py3-pip
RUN apk add mariadb-client
COPY ./configure.py /tmp/
COPY . /tmp/
COPY ./requirements.txt /tmp/
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip3 install --root-user-action=ignore -r /tmp/requirements.txt --use-pep517
COPY ./configure.py /usr/bin/databasemigrator
RUN chmod +x /usr/bin/databasemigrator
ENTRYPOINT ["databasemigrator"]
