FROM python:3.9.10
# Set the working directory to /app
WORKDIR /praca
# Copy local contents into the container
ADD . /praca
# Install all required dependencies
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]