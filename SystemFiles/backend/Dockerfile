FROM python:3.6

MAINTAINER tien.sp@gmail.com

COPY requirements.txt env ./
RUN pip install -r requirements.txt

WORKDIR /cron
ADD mycron /cron
ADD do.sh /cron

RUN apt-get update
RUN apt-get install -y cron
RUN apt-get install -y libopencv-dev python3-pip python3-opencv

RUN touch /cron/cron.log

RUN chmod +x /cron/do.sh
RUN chmod 0600 /cron/mycron

# RUN crontab -u root /cron/mycron

ENTRYPOINT ["cron", "-f"]