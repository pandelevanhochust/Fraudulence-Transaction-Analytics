FROM python:3.11-slim
LABEL authors="pandelevan"

WORKDIR /app
COPY server.py /app/server.py
#COPY requirement.txt  /app/requirement.txt
#RUN pip install -r requirement.txt

ENV PYTHONUNBUFFERED = 1
ENV PORT=5050

EXPOSE 5050
CMD ["python","server.py"]
