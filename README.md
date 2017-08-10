# GreenToGo

This project contains both the GreenToGo mobile app and the Django web application with an API.

The files are laid out in accordance with recommendations from Two Scoops of Django.

## Django setup

1. This application uses Python 3.6, so ensure you have that installed.
1. Setup PostgreSQL. On a Mac with Homebrew, run `brew install postgresql`. If you are on a Mac without Homebrew, download and install [Postgres.app](https://postgresapp.com/). If you are on Windows, see https://www.postgresql.org/download/windows/. If you are on Linux, you know what to do.
1. Make sure you have the following installed:
   - bower: `npm install -g bower`
   - gpg: depends on your OS. `brew install gpg` on Mac.
   - node-sass: `npm install -g node-sass`
1. Make sure you are in a virtualenv. Using [direnv](https://direnv.net/) is a very easy way to make this happen.
1. Install pip-tools: `pip install pip-tools`.
1. Run `make requirements`. If that worked, you should be ready for the next part!
1. Run `make greentogo/greentogo/.env`. This will decrypt a file that contains the API keys you will need. If you need the password, ask Erin or Clinton.
1. Run `./greentogo/manage.py migrate`.

## Docs for libraries used

* [Wagtail Menus](https://github.com/rkhleics/wagtailmenus)
