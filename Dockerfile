FROM python:3.6
EXPOSE 5000

COPY . /app
WORKDIR /app

RUN pip3 install .

ENTRYPOINT ["python"]
CMD ["app.py"]
