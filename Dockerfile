FROM python:2-onbuild
CMD gunicorn -b 0.0.0.0:8000 bencast:app
