Web App
===========

Bootstrapped with [makesite.py](https://github.com/sunainapai/makesite), [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/) and [voila](https://voila.readthedocs.io/en/stable/)

## Prerequisites:
- Python 3
- Voila

  ```
  $ pip install voila
  ```

## Local deployment
1. Build the site locally, which will be created under `_site` directory
   ```
   $ cd SystemFiles/webapp
   $ python makesite.py
   ```

2. Host the website locally
   ```
   $ cd SystemFiles/webapp/_site
   $ python -m http.server
   ```

3. Run Voila. It is used to preview ipynb notebooks in the webapp.
   ```
   $ cd SystemFiles/

   ## Add CORS policy:
   $ voila --Voila.tornado_settings="{'headers':{'Content-Security-Policy': 'frame-ancestors \'self\' http://localhost:8000'}}"
   ```
