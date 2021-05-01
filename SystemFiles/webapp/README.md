
# Navigate to the webapp folder

```
$ (Unix/Mac) cd SystemFiles/webapp
$ (Windows) cd "SystemFiles\webapp"
$ (Powershell) cd "SystemFiles\webapp"
```

# Install modules
```
$ pip3 install -r requirements.txt
```

# Set the FLASK_APP environment variable
```
$ (Unix/Mac) export FLASK_APP=run.py
$ (Windows) set FLASK_APP=run.py
$ (Powershell) $env:FLASK_APP = ".\run.py"
```

# Set up the DEBUG environment
```
$ (Unix/Mac) export FLASK_ENV=development
$ (Windows) set FLASK_ENV=development
$ (Powershell) $env:FLASK_ENV = "development"
```

# Start the application (development mode)
```
# --host=0.0.0.0 - expose the app on all network interfaces (default 127.0.0.1)
# --port=5000    - specify the app port (default 5000)
$ flask run --host=0.0.0.0 --port=5000
```

# Access the dashboard in browser: 
```
    http://127.0.0.1:5000/
```

