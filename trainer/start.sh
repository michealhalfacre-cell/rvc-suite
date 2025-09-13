#!/bin/bash
echo "Launching JupyterLab for RVC training..."
pip install jupyterlab
jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --no-browser