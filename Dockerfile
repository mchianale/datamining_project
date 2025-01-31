# Use Alpine-based Python image
FROM python:3.10-slim

# Set the working directory to /app inside the container
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app

# Command to run the application with automatic reload
CMD ["uvicorn", "app.main:app","--host", "0.0.0.0"]