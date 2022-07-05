FROM python:3.9.10
# Set the working directory to /app
WORKDIR /praca
# Copy local contents into the container
COPY . .
# Install all required dependencies
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]