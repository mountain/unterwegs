#!/bin/bash

celery -A unterwegs.celery worker -l INFO
