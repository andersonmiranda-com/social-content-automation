#!/bin/bash
pipenv requirements > requirements.txt
pipenv requirements --dev > requirements-dev.txt
echo "requirements.txt y requirements-dev.txt actualizados."