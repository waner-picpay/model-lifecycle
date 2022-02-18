FROM python:3.9

VOLUME [ "/opt/app" ]
WORKDIR /opt/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
# RUN pip install --upgrade pip
ENTRYPOINT /bin/bash 
# CMD ["/bin/bash"]
# RUN pip install --no-cache-dir -r requirements.txt


# # running migrations
# RUN python manage.py migrate

# # gunicorn
# CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

