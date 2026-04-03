#!/bin/bash
pip install pip-review
pip-review --auto
pip uninstall pip-review -y
pip freeze > requirements.txt
