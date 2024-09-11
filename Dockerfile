FROM python:3.11-alpine

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1


RUN apk --no-cache add \
    icu-dev \
    gettext \
    gettext-dev

RUN apk add gcc python3-dev musl-dev linux-headers

RUN apk --no-cache add glib-dev poppler-glib vips-dev vips-tools poppler-utils ffmpeg
RUN apk add gettext
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip

RUN pip install -r requirements.txt


# Copy project
COPY . .

# Expose the port
EXPOSE 8000

# run entrypoint.prod.sh
# RUN ["chmod", "+x", "/app/entrypoint.sh"]
# ENTRYPOINT ["sh", "/app/entrypoint.sh"]