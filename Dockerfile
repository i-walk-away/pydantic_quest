FROM ubuntu:latest
LABEL authors="iwalkaway"

ENTRYPOINT ["top", "-b"]