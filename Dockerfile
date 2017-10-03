FROM python:3.6
EXPOSE 5000
VOLUME ["/var/db"]

COPY . /app
WORKDIR /app

RUN pip3 install .

ENV TITLEGEN_DB="/var/db/titlegen.db"
ENTRYPOINT ["python"]
CMD ["app.py"]
