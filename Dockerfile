FROM ubuntu:18.04
RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
	PIP_INSTALL="python -m pip --no-cache-dir install --upgrade" && \
	GIT_CLONE="git clone --depth 10" && \
	apt update && \
	DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
		python3.6 \
		python3-setuptools \
		python3-pip \
		git \
		&& \
	ln -s /usr/bin/python3.6 /usr/local/bin/python && \
	ln -s /usr/bin/pip3 /usr/local/bin/pip && \
	$PIP_INSTALL \
		flask \
		pyyaml \
		websocket_server \
		websocket-client \
		requests \
		&& \
	ldconfig && \
	apt-get clean && \
	apt-get autoremove
WORKDIR /root
COPY . .
#WORKDIR /root/src
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
CMD ["python", "src/main.py"]
