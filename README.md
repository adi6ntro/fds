# Welcome to FDS!

This is an template of FDS.

## Installation

Create a Python 3 virtual environment

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ _
```

Then, install every necessary python module

```bash
$ pip install -r requirements.txt
```

## Usage

Setting the `FLASK_APP` environment variable

```bash
# use set instead of export if you are using windows
(venv) $ export FLASK_APP=app.py
(venv) $ export FLASK_ENV=development
```

Finally, run the apps

```bash
(venv) $ flask run
 * Serving Flask app "app.py"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Simplify

Once venv folder created. Make an .flaskenv or .env file of this:

```bash
FLASK_APP=app.py
FLASK_ENV=development
```

Then, you will be simply run by this:

```bash
$ source venv/bin/activate
(venv) $ flask run
 * Serving Flask app "app.py"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
