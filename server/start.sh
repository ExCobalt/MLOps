#!/bin/bash
python support/load_to_postgres.py
gunicorn --bind 0.0.0.0:5000 main:app