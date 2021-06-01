FROM python:3.8.6-buster

COPY app.py /app.py
COPY data /data
COPY setup.sh /setup.sh
COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD sh /setup.sh && streamlit run app.py
