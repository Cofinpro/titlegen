FROM python:3.6
EXPOSE 5000

COPY . /app
WORKDIR /app

RUN pip3 install .

ENV DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/postgres"
ENTRYPOINT ["python"]
CMD ["app.py"]
