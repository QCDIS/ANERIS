FROM hariszaf/pema:v.2.1.4

ARG API_REQ_FOLDER

WORKDIR /api
# --chown=root:root
COPY ${API_REQ_FOLDER?}/ ./
RUN pip install -r ./requirements.txt

RUN chmod -R +777 ./modules ./pema_latest.bds
RUN cp -rf ./modules /home/ &&\
    cp -rf ./pema_latest.bds /home/

WORKDIR /home
CMD ["fastapi", "run", "/api/main.py", "--port", "80"]
