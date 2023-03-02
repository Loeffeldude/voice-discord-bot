FROM ubuntu

RUN apt install -y python3 && \
		apt install -y python3-pip && \
		apt install -y mpg123 && \
		apt install -y libopus0

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]

