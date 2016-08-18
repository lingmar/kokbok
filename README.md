# kokbok

## Setting up virtualenv
1. `mkvirtualenv --python=/usr/bin/python3 kokbok`
2. `workon kokbok`

## Configuring DB connections

Set the following environment variables:

```
KOK_DB_NAME="kokbok"
KOK_DB_HOST="localhost"
KOK_DB_PORT="3306"
KOK_DB_USER="root"
KOK_DB_PASSWORD=""
```

It is recommended to `export` these settings in the file `.env` (which
will be ignored by Git) and load them using `source .env`.

## Installing dependencies
`pip3 install -r requirements.txt`
