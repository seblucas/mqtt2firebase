FROM seblucas/alpine-python3:latest
LABEL maintainer="Sebastien Lucas <sebastien@slucas.fr>"
LABEL Description="mqtt2firebase image"

RUN pip3 install firebase-admin

COPY *.py /usr/bin/

RUN chmod +x /usr/bin/mqtt2firebase.py

ENTRYPOINT ["/bin/sh"]
