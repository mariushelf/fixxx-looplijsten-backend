FROM amsterdam/python
LABEL maintainer="datapunt@amsterdam.nl"

ENV PYTHONUNBUFFERED 1
ARG INTEGRALE_AANPAK_ONDERMIJNING_CREDS
ARG INTEGRALE_AANPAK_ONDERMIJNING_PERSONAL_ACCESS_TOKEN
ARG ONDERHUUR_MODEL_CREDS
ARG ONDERHUUR_MODEL_PERSONAL_ACCESS_TOKEN

# Setup Certificates for ADP/Motiv
COPY certificates/adp_rootca.crt /usr/local/share/ca-certificates/extras/adp_rootca.crt
RUN chmod 644 /usr/local/share/ca-certificates/extras/adp_rootca.crt \
  && update-ca-certificates --fresh

# Setup datapunt directories and user
RUN adduser --system datapunt
ENV DIRECTORYLIST "/static /app /downloads /certificates /deploy /var/log/uwsgi /fraud_prediction_cache"
RUN mkdir -p ${DIRECTORYLIST} && chown datapunt ${DIRECTORYLIST}

# Setup application
WORKDIR /app
COPY requirements.txt /app/

RUN mkdir /tmp/integrale_aanpak_ondermijning
RUN mkdir /tmp/onderhuur_model

ARG INTEGRALE_AANPAK_ONDERMIJNING_VERSION=v1.2.0
# Clone the private cto-fraude-aanpak library using a deploy token
RUN if [ "x$INTEGRALE_AANPAK_ONDERMIJNING_CREDS" = "x" ] ; then echo INTEGRALE_AANPAK_ONDERMIJNING_CREDS not provided ; else git clone -b ${INTEGRALE_AANPAK_ONDERMIJNING_VERSION} --single-branch https://${INTEGRALE_AANPAK_ONDERMIJNING_CREDS}@git.data.amsterdam.nl/cto-fraude-aanpak/integrale_aanpak_ondermijning /tmp/integrale_aanpak_ondermijning ; fi

# Clone the private cto-fraude-aanpak library using a personal access token
RUN if [ "x$INTEGRALE_AANPAK_ONDERMIJNING_PERSONAL_ACCESS_TOKEN" = "x" ] ; then echo INTEGRALE_AANPAK_ONDERMIJNING_CREDS not provided ; else git clone -b ${INTEGRALE_AANPAK_ONDERMIJNING_VERSION} --single-branch https://oauth2:${INTEGRALE_AANPAK_ONDERMIJNING_PERSONAL_ACCESS_TOKEN}@git.data.amsterdam.nl/cto-fraude-aanpak/integrale_aanpak_ondermijning /tmp/integrale_aanpak_ondermijning ; fi


# Clone the private cto-onderhuur library using a deploy token
RUN if [ "x$ONDERHUUR_MODEL_CREDS" = "x" ] ; then echo ONDERHUUR_MODEL_CREDS not provided ; else git clone -b bwv_branch --single-branch https://${ONDERHUUR_MODEL_CREDS}@git.data.amsterdam.nl/cto-fraude-aanpak/onderhuur-adreskwaliteit-backend /tmp/onderhuur_model ; fi

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install uwsgi
RUN if [ "x$INTEGRALE_AANPAK_ONDERMIJNING_CREDS$INTEGRALE_AANPAK_ONDERMIJNING_PERSONAL_ACCESS_TOKEN" = "x" ] ; then pip install --no-cache-dir -r requirements.txt ;  else pip install --no-cache-dir -r requirements.txt /tmp/integrale_aanpak_ondermijning ; fi
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -I shap==0.38.1

COPY . /app/
COPY deploy /deploy/

RUN chmod +x /app/wait-for.sh
RUN chmod +x /app/celery.sh
RUN chmod +x /app/celery-beat.sh

CMD ["/deploy/entrypoint.sh"]
