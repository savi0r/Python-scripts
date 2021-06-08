FROM python:3
ADD metrics.py /
ADD requirements.txt /
RUN pip install -r /requirements.txt
CMD [ "python", "./metrics.py" ]
