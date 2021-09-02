FROM ubuntu:16.04

MAINTAINER Manh Nguyen Duc (manh.nguyenduc@campus.tu-berlin.de)
LABEL Description="SR Hackathon 2021 integration Dockerised Simulation of Urban MObility(SUMO)"

ENV SUMO_VERSION 0.31.0
ENV SUMO_HOME /opt/sumo
ENV SUMO_USER srh21

# Install system dependencies.

RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
	PIP3_INSTALL="python3 -m pip --no-cache-dir install --upgrade" && \
	GIT_CLONE="git clone --depth 10" && \
	apt update && \
	DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        wget \
        g++ \
        make \
        libxerces-c-dev \
        libfox-1.6-0 libfox-1.6-dev \
        python2.7 \
		python3.6 \
		python3-setuptools \
		python3-pip \
		git \
		&& \

	$PIP3_INSTALL \
		flask \
		pyyaml \
		websocket_server \
		websocket-client \
		requests \
		&& \
	ldconfig && \
	apt-get clean && \
	apt-get autoremove

# Download and extract source code
RUN wget http://downloads.sourceforge.net/project/sumo/sumo/version%20$SUMO_VERSION/sumo-src-$SUMO_VERSION.tar.gz
RUN tar xzf sumo-src-$SUMO_VERSION.tar.gz && \
    mv sumo-$SUMO_VERSION $SUMO_HOME && \
    rm sumo-src-$SUMO_VERSION.tar.gz

# Configure and build from source.
RUN cd $SUMO_HOME && ./configure && make -j$(nproc) && make install

RUN adduser $SUMO_USER --disabled-password
# CMD sumo-gui

USER srh21
WORKDIR /root
COPY . .
WORKDIR /root/src
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
CMD ["python3", "main.py"]