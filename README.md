# facebook-currency-bot

This repository contains simple chatbot web application for the Facebook, which is capable of converting money amounts between different currencies as well as displaying various currency exchange rates. The latter are updated daily into MySQL database using external source (https://www.exchangerate-api.com/docs/free). The communication between user and the application is done via Facebook Messenger using console-like commands.


External libraries used:
- flask
- flask-sqlalchemy
- requests


Contents of the repository:
- bots. Contains Facebook API-specific bot class for processing all communication with user via Messenger.
- database. Basic database settings (db_setup.py) and update task (db_update.py) intended to be sheduled.
- security. For security reasons credential information (passwords and Facebook access token) are stored separately from the application.
- templates. Folder for page templates. Contains license page required by Facebook.
- logs. The folder is created as necessary by the apllication.
