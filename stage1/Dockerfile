FROM python:3
ADD web.py script.py requirements.txt out.txt template.html /
RUN pip install -r /requirements.txt
CMD [ "python", "./web.py" ]
