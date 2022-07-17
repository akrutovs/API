FROM python:3.9
WORKDIR /application
COPY . /application
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "main.py"]