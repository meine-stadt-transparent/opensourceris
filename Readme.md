# Meine Stadt Transparent

[![Travis](https://img.shields.io/travis/meine-stadt-transparent/meine-stadt-transparent/master.svg?style=flat-square)](https://travis-ci.org/meine-stadt-transparent/meine-stadt-transparent)
[![Code Climate](https://codeclimate.com/github/meine-stadt-transparent/meine-stadt-transparent/badges/gpa.svg)](https://codeclimate.com/github/meine-stadt-transparent/meine-stadt-transparent)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent?ref=badge_shield)
[![Docker Build Status](https://img.shields.io/docker/build/konstin2/meine-stadt-transparent.svg?style=flat-square)](https://hub.docker.com/r/konstin2/meine-stadt-transparent/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/ambv/black)

Meine Stadt Transparent is a free council information system. Its current main focus is presenting data from offical German council information systems, so called "Ratsinforamtionssysteme". Those are imported using the [OParl](https://oparl.org) API, which can easily customized. You can even write your own importer for arbitrary data sources.

Our sample live system using the data of the city [Jülich](https://www.juelich.de/) is available at: [https://meine-stadt-transparent.de/](https://meine-stadt-transparent.de/).

The project was sponsored by the [Prototype Fund](https://prototypefund.de/).

![Logo of the Prototype Fund](etc/prototype-fund-logo.svg) ![Gefördert von Bundesministetrium für Bilduung und Forschung](etc/bmbf-logo.svg) ![Logo of the Open Knowledge Foundation Germany](etc/okfde-logo.svg)

## About this project

Meine Stadt Transparent makes decision-making in city councils and administrations more transparent by providing easy access to information about the city council, including published documents, motions and meeting agendas. As a successor to Munich's [München Transparent](https://www.muenchen-transparent.de/), its aim is to be easily deployable for as many cities as possible.

It includes many features regarding data research and staying up to date, targeted both towards citizens and journalists:

- Information about city councillors, administrative organizations and meetings of the city council are provided.
- All published documents are searchable in a flexible manner, be it motions, resolutions, meeting agendas or protocols. The search supports both simple full-text searchs and flexible criteria-based filters.
- Documents are automatically searched for mentioned places. A map is provided indicating places that are mentioned. Thus, it is easy to identify documents that affect places in your living neighborhood.
- You can subscribe to topics / search expressions to get notified by e-mail, once new documents matching your query are published.
- It supports several ways of subscribing to new content: different kinds of RSS-feeds and subscribing to the meeting calendar using the iCal-format.
- We try to make Meine Stadt Transparent accessible by everyone: the layout is responsive to provide a good experience on mobile device, and we follow accessibility standards (WCAG 2.0 AA, ARIA) as close as possible.

Meine Stadt Transparent is *not* a complete replacement for traditional council information systems, however: it focuses on displaying already published information to the public. It does not provide a user-accessible backend for content authoring. It relies on the availability of an API provided by a council information system backend. Currently, the open [Oparl-Standard](https://oparl.org/) is supported.

# Production setup with docker compose

Prerequisites: A host with root access and enough ram for elasticsearch and mariadb.

All services will run in docker containers orchestrated by docker compose, with nginx as reverse proxy in front of them which also serves static files.

First, install [docker](https://docs.docker.com/install/) and [docker compose](https://docs.docker.com/compose/install/). You'll likely need to [adjust max_map_count](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode) on the host system for elasticsearch.

Download [etc/docker-compose.yml](etc/docker-compose.yml) from the root of this repository. Replace all `changeme` with real random passwords (Hint: `openssl rand -hex 32`).

Download [etc/env-template](etc/env-template) to `.env`. Change `REAL_HOST` to your domain, `SECRET_KEY` to a randomly generated secret and use the same passwords as in `docker-compose.yml` for `DATABASE_URL`, and `MINIO_SECRET_KEY`. You most likely want to configure third-party services as described later, but you can postpone that until after the base site works.

To deliver the assets through nginx, we need to mount them to a local container:

```
mkdir /var/www/meine-stadt-transparent-static
docker volume create --opt type=none --opt device=/var/www/meine-stadt-transparent-static --opt o=bind django_static
```

You can change the directory to any other as long as you match that later in your nginx conf.

Start everything:

```
docker-compose up
```

Wait until the elasticsearch log says `Cluster health status changed from [RED] to [YELLOW]` and open another terminal. You can later start the services as daemons with `-d` or stop them with `docker-compose down`.

Then we can run the migrations:

```
docker-compose run --rm django ./manage.py migrate
```

Let's load some dummy data to check everythings wokring:

```
docker-compose run --rm django ./manage.py loaddata mainapp/fixtures/initdata.json
```

You should now get a 200 response from [localhost:8000](http://localhost:8000).

If you've not familiar with nginx, you should start with [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04).  Install nginx, [certbot](https://certbot.eff.org/) and the certbot nginx integration. For ubuntu it is e.g.

```
sudo add-apt-repository ppa:certbot/certbot
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

Download [etc/nginx-http.conf](etc/nginx-http.conf), add it to your nginx sites and replace `changeme.tld` with your domain. Then run certbot and follow the instructions:

```
certbot --nginx
```

Certbot will rewrite the nginx configuration to a version with strong encryption. You might also want to activate http/2 by adding `http2` after both `443 ssl`.

You now have a proper site at your domain!

Now that everything is in place, drop the dummy data:

```
docker-compose run --rm django ./manage.py flush
```

Instead, import real data by replacing `Springfield` with the name of your city. See [docs/Import.md](docs/Import.md) for details.

```
docker-compose run --rm django ./manage.py import Springfield
```

You should now have a usable instance!

Finally, create a daily cronjob with the following. This will import changed objects from the oparl api and then notify the users. Also make sure that there is a cronjob for certbot.

```
docker-compose run --rm django ./manage.py cron
```

You can execute all the other commands from this readme by prepending them with `docker-compose run --rm django` (or starting a shell in the container). Note for advanced users: `.venv/bin/python` is configured as entrypoint.

Next, have a look at [docs/Customization.md](docs/Customization.md).

### Updates

After pulling a new version of the docker container, you need to run the following commands to update the assets:

```
docker-compose down
rm -r /var/www/meine-stadt-transparent-static
mkdir /var/www/meine-stadt-transparent-static
docker-compose up
```

## Manual Setup

### Requirements

 - Python 3.5, 3.6 or 3.7 with pip and [poetry](https://github.com/sdispater/poetry)
 - A recent node version (8 or 10) with npm (npm 6 is tested)
 - A webserver (nginx or apache is recommended)
 - A Database (MariaDB is recommended, though anything that django supports should work)
 - If you want to use elasticsearch, you either need [docker and docker compose](https://docs.docker.com/engine/installation/) or will have to [install elasticsearch 5.6 yourself](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/_installation.html)

On Debian/Ubuntu:

```
sudo apt install python3-pip python3-venv python3-gi python3-dev nodejs json-glib-1.0 gir1.2-json-1.0 \
    git libmysqlclient-dev libmagickwand-dev poppler-utils tesseract-ocr libssl-dev
```

Install dependencies.

```
poetry config settings.virtualenvs.in-project true # This is not mandatory, yet quite useful
poetry install
npm install
```

Activate the virtualenv created by poetry. You either need to run this in your shell before running any other python command or prefix any python command with `poetry run`.

```
poetry shell
```

Copy [etc/env-template](etc/env-template) to `.env` and adjust the values. You can specify a different dotenv file with the `ENV_PATH` environment variable.

Configure your webserver, see e.g. [etc/nginx.conf](etc/nginx.conf)

### pygobject (gi) and liboparl

This is currently only required to use the importer. You can skip it if you don't use the importer.

pygobject needs to be installed system-wide and only works with the system python. If you have any better solution for using a vala library in python we would be extremely happy to use it.

 -  Debian/Ubuntu:
    ```
    sudo apt install python3-gi
    ln -s /usr/lib/python3/dist-packages/gi .venv/lib/python*/site-packages/
    ```

 -  macOS:
    ```
    brew install pygobject3 --with-python3
    # Replace 3.26.0 and projectdir by the real paths
    ln -s /usr/local/Cellar/pygobject3/3.26.0/lib/python3.6/site-packages/* .venv/lib/python3.6/site-packages/
    ```

Try `python3 -c "import gi"` inside your virtualenv to ensure everything is working.

For liboparl, clone the [https://github.com/OParl/liboparl](https://github.com/OParl/liboparl) and follow the installation instructions. Be sure to use `--prefix=/usr --buildtype=release` on `meson`.

### Production

The following steps are only required when you want to deploy the site to production. For development, see the corresponding section below

 ```
npm run build:prod
npm run build:email
./manage.py collectstatic
 ```

Follow the [the official guide](https://docs.djangoproject.com/en/1.11/howto/deployment/). Unlike the guide, we recommend gunicorn over wsgi as gunicorn is much simpler to configure.

The site is now ready :tada:. Next, have a look at [docs/Customization.md](docs/Customization.md) and [docs/Import.md](docs/Import.md).

### Development

Please refer to [docs/Development.md](docs/Development.md)

## Known Problems

If you hit problems regarding memory when starting elasticsearch, please have a look at this
[documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-cli-run-prod-mode).

If MySQL/MariaDB is to be used as a database backend, a Version of at least 5.7 (MySQL) or 10.2 (MariaDB) is needed,
with Barracuda being set as the default format for new InnoDB-Tables (default), otherwise you will run into errors about too long Indexes.

## License

This software is published under the terms of the MIT license. The json files under `mainapp/testdata/oparl` are adapted from the oparl project and licensed under CC-BY-SA-4.0. The license of the included animal pictures `mainapp/testdata/oparl` are CC0 and CC-BY-SA Luigi Rosa. The redistribution of `etc/Donald Knuth - The Complexity of Songs.pdf` is explicitly allowed in its last paragraph.

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fmeine-stadt-transparent%2Fmeine-stadt-transparent?ref=badge_large)
