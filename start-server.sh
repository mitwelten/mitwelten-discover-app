#!/bin/sh

uvicorn main:app --port 8000 --log-config log_conf.yaml --reload
