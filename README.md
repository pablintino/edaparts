# edaparts (EDA components management service)

This repo contains an API that manages EDA (Electronic Design Automation) parts. Now with component inventory too!  
The API has been build using python 3.12 and all the FastAPI ecosystem, that means sqlalchemy and migrations are
used behind the scenes.

Fully usable with EDA tools like Altium or KiCAD (with HTTP and database library types)

## Environment

The application is meant to be run as a Docker container. In order to configure the container the following environment
variables can be used:

- DB_CONNECTION_STRING: Database URI. This application is meant to be used with a PostgreSQL database, so this URI would
  be likely similar to this one:  
  ```postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}```
- DB_USER: If `DB_CONNECTION_STRING` is not given this is the user that will be used in the default connection string.
- DB_PASSWORD: If `DB_CONNECTION_STRING` is not given this is the password that will be used in the default connection
  string.
- DB_HOST: If `DB_CONNECTION_STRING` is not given this is the DB host that will be used in the default connection
  string.
- DB_NAME: If `DB_CONNECTION_STRING` is not given this is the database name that will be used in the default connection
  string.
