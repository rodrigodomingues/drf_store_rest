FROM amazonlinux:2

ARG BUILD_VERSION
ARG dest=/opt

ENV BUILD_VERSION=$BUILD_VERSION
ENV PYTHONPATH ${dest}

# Install the basics and base packages
RUN yum -y update && \
    yum -y install yum-utils && \
    yum -y groupinstall development

# Tools
RUN yum -y install \
    vim

# Morcilla uses Python 3 and some tools
RUN yum -y install \
    python3 \
    python3-devel \
    python3-pip \
    git \
    curl \
    gettext

# Fix issue with setuptools versions.
# Issue here: https://github.com/pypa/setuptools/issues/1257
RUN pip3 install setuptools==38.5.1

RUN amazon-linux-extras install postgresql9.6

WORKDIR ${dest}

# Python dependencies in WORKDIR (curr_dir)
COPY ./*requirements.txt ./
RUN pip3 install -r ./requirements.txt && rm ./requirements.txt \
    && pip3 install -r ./test-requirements.txt && rm ./test-requirements.txt

RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

COPY ./ ${dest}

#expose ports for http (8080)
EXPOSE 8080

CMD ["scripts/start.sh"]
