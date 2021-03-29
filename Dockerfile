FROM python:3.6
WORKDIR /Project/demo

COPY env/requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "manage:app", "--log-level=debug", "-c", "./gunicorn.conf.py"]

# docker run -d -p 80:80 --name=flask testflask