FROM python:latest

WORKDIR /app

# RUN mkdir -p /static_folder
COPY ./src .

# RUN echo "hello" > index.html

CMD ["python", "-m", "http.server", "8000"]

#docker build -f Dockerfile -t pyapp .