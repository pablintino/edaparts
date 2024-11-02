#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#

FROM tiangolo/uwsgi-nginx-flask:python3.8

# Set FLASK APP used mainly for migrations
ENV FLASK_APP='app/wsgi.py'
ENV REDIS_URL='redis://'
ENV NODE_TYPE='web'
ENV REPO_PATH='/altium-repo'
ENV SSH_HOSTS_FILE=''
ENV SSH_IDENTITY='/ssh-dir/id_rsa'

VOLUME repo-vol:/altium-repo
VOLUME ssh-vol:/ssh-dir

COPY requirements.txt /tmp/

# Add all required packages and mssql tools
RUN apt-get update && apt-get install -y gcc libc-dev unixodbc-dev curl apt-utils apt-transport-https debconf-utils \
 build-essential libssl1.1 libssl-dev ca-certificates unixodbc-dev && rm -rf /var/lib/apt/lists/* && \
 curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - &&\
 curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
 apt-get update && ACCEPT_EULA=Y apt-get install -y  msodbcsql17 && \
 pip install -U pip && pip install -r /tmp/requirements.txt


# Override parent image supervidord configuration and start script
RUN mv /etc/supervisor/conf.d/supervisord.conf /etc/supervisor/conf.d/supervisord-web-node.conf
COPY sources/supervisord-worker-node.conf /etc/supervisor/conf.d/supervisord-worker-node.conf
COPY sources/start.sh /start.sh
RUN chmod +x /start.sh


# Copy source code
WORKDIR /app
COPY ./sources /app
