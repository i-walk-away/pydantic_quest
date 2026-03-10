FROM ghcr.io/engineer-man/piston:latest

ENV PISTON_RUNTIME_LANGUAGE=python \
    PISTON_RUNTIME_VERSION=3.12.0 \
    PISTON_RUNTIME_PYDANTIC_SPEC='pydantic>=2.12,<3' \
    PISTON_RUNTIME_INSTALL_ATTEMPTS=3

COPY docker/piston/install-runtime.js /opt/piston/install-runtime.js
COPY docker/piston/bootstrap.sh /opt/piston/bootstrap.sh

RUN chmod +x /opt/piston/bootstrap.sh
