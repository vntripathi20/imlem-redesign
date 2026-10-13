"""IMLEM website entry point.

    flask --app app run                      # development
    gunicorn app:app / waitress-serve app:app   # production behind HTTPS (see DEPLOYMENT.md)

The application itself lives in the ``imlem_site`` package.
"""
import os

from imlem_site.web import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT', 5000)),
            debug=app.config['DEBUG'])
