# GreenToGo

This project contains both the GreenToGo mobile app and the Django web application with an API.

The files are laid out in accordance with recommendations from Two Scoops of Django.

## Django setup

1. This application uses Python 3.6, so ensure you have that installed.
1. Setup PostgreSQL. On a Mac with Homebrew, run `brew install postgresql`. If you are on a Mac without Homebrew, download and install [Postgres.app](https://postgresapp.com/). If you are on Windows, see https://www.postgresql.org/download/windows/. If you are on Linux, you know what to do.
1. Make sure you are in a virtualenv. Using [direnv](https://direnv.net/) or [pyenv-installer](https://github.com/pyenv/pyenv-installer) is a very easy way to make this happen.
1. Run `make check` to make sure you have all the required programs installed.
1. Run `make requirements`. If that worked, you should be ready for the next part!
1. Run `make greentogo/greentogo/.env`. This will create a file to hold the database URL and API keys that you will need. (See "Environment Setup" below.)
1. Run `./greentogo/manage.py migrate`.

## Environment setup

Database configuration and API keys are held in `greentogo/greentogo/.env`, which can be created by running `make greentogo/greentogo/.env`. The `.env` file looks like the following:

```
DEBUG=1
DATABASE_URL=postgres://user@/greentogo
EMAIL_ADDRESS=purchases@durhamgreentogo.com
EMAIL_REPLY_TO=info@durhamgreentogo.com
GOOGLE_API_KEY=ADD_KEY_HERE
STRIPE_SECRET_KEY=ADD_KEY_HERE
STRIPE_PUBLISHABLE_KEY=ADD_KEY_HERE
STRIPE_WEBHOOK_SECRET=ADD_KEY_HERE
ROLLBAR_KEY=ADD_KEY_HERE
```

For `DATABASE_URL`, change this to match your local database setup. If you have a local database named `greentogo` owned by your user account, you should be able to replace `user` with your own username and be set up.

For the Stripe keys, you will need to create an account at [Stripe](https://stripe.com/). Once you have an account, you can get your secret and publishable keys at <https://dashboard.stripe.com/account/apikeys>. For development, you can ignore `STRIPE_WEBHOOK_SECRET` and `ROLLBAR_KEY`.

For your Google API key, you can generate a key at <https://console.developers.google.com/apis/credentials>. This key will need access to the Google Maps API. However, you can also ignore this in development unless working on part of the application that uses maps.
