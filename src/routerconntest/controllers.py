from flask import render_template
import json

from routerconntest import app
from routerconntest.models import generate_route


# Render: index.html
@app.route('/')
def render_index():
    print('>> Render: index.html')
    return render_template('index.html')


# @app.route(url)
# def render_...()

# Respond: From button click
@app.route('/update', methods=['GET'])
def respond_update():
    print('>> Request: (url)/update')

    data_route = generate_route()
    json_route = json.dumps(data_route)

    response = app.response_class(
        response=json_route,
        status=200,
        mimetype='application/json'
    )

    print('>> Response: %s' % json_route)

    return response

# @app.route(url, methods)
# def respond_...()
