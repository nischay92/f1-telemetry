FROM python:3.12

WORKDIR /app

COPY . .

# Copy common requirements.txt from parent
COPY ../requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
