FROM python:3.9

RUN pip install --upgrade pip

RUN mkdir -p /opt/app/
COPY ./requirements.txt /opt/app/
VOLUME [ "/opt/app" ]
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies


RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /opt/app
RUN python manage.py migrate

# CMD ["/bin/bash"]

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
# # running migrations

# # gunicorn
# CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

