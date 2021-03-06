FROM seblucas/alpine-python3:latest
LABEL maintainer="Sebastien Lucas <sebastien@slucas.fr>"
LABEL Description="mqtt2firebase image"

COPY requirements.txt /tmp

RUN pip3 install -r /tmp/requirements.txt

COPY *.py /usr/bin/

RUN chmod +x /usr/bin/mqtt2firebase.py

ENTRYPOINT ["python3", "-u", "/usr/bin/mqtt2firebase.py"]
CMD ["--help"]

