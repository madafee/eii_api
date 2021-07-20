FROM docker.dlyunzhi.cn:7114/common/python:3.7

MAINTAINER liuxu <liuxu0909@163.com>

ARG BASE_NAME
ENV BASE_NAME=$BASE_NAME

# create workspace
RUN mkdir -p /opt/$BASE_NAME/project \
&& mkdir -p /opt/config \
&& mkdir -p /opt/log \
&& mkdir -p /opt/data \
&& mkdir -p /opt/temp \
&& mkdir -p /opt/lib

RUN apt-get update && \
apt-get install -y \
libpq-dev

# install python package
RUN pip3 install --upgrade pip -i https://pypi.douban.com/simple
RUN pip3 install meinheld \
gunicorn \
Flask \
Flask-RESTful \
Flask-SQLAlchemy \
Flask-CORS \
flask_doclever \
itsdangerous \
passlib \
PyMySQL \
requests \
jsonschema \
gevent \
\
sentry-sdk[flask] \
xpinyin \
xlsxwriter \
openpyxl \
flask_apscheduler \
-i https://pypi.douban.com/simple

RUN pip3 install --upgrade pycryptodome flask_doclever

# cleaning
RUN apt-get autoremove -y --purge make gcc \
python3-dev libxml2-dev libreadline-dev build-essential && \
apt-get clean && \
rm -rf /var/lib/apt/lists/* && \
rm -rf /opt/temp/*

# port
# flask_restful
EXPOSE 5000

# timezone
RUN echo "Asia/Shanghai" > /etc/timezone && \
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# deploy the service
ADD project /opt/$BASE_NAME/project
ADD run.py /opt/$BASE_NAME/
RUN pyconcrete-admin.py compile --source=/opt/$BASE_NAME/ \
--pye --remove-py --remove-pyc -i run.py
ADD docker/entrypoint.sh /opt/entrypoint.sh
RUN chmod 777 /opt/entrypoint.sh

WORKDIR /opt/

# run process with supervisor
CMD ["/opt/entrypoint.sh"]
