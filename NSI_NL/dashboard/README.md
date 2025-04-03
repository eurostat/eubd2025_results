
# Air Inequity Index Dashboard
This is a simple dashboard written in Python Dash. It displays data retrieved from a Postgres Database.

We unfortunately do not have code showing how to set up such database as it was already available during the Hackathon,
but we do have a script for inserting geospatial data. This is found in `/scripts/shape_to_postgres.py`.

## Running the Dash Dashboard

### 1. Make a virtual environment (Optional)

First make a Python virtual environment with `venv` and activate it.
```
python3 -m venv venv && \
source venv/bin/activate
```

### 2. Install dependencies

```
pip install -r ./requirements.txt
```

### 3. Configure database settings (IMPORTANT)
Configure the database settings in `config.py`.
Make sure to enter the correct authentication credentials.

### 4. Run the app from command line

```
python3 app.py
```

