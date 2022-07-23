################################################################################
# Define package composition
################################################################################

__all__ = []

from flask import g, render_template, request, session, redirect
from oap import app

@app.route('/')
def root_get():
    """GET /"""
    return render_template('index.html')