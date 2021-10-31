FROM python:3.9
COPY src /app
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "./runner.py"]