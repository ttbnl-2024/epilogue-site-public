# Deployment

Instructions for setting this website up on Heroku.
If you want to use a different platform, good luck!
Some concepts may be similar, but this is pretty Heroku-specific.

We've also written about the MH24 epilogue's tech in the [wrapup](https://epilogue.mitmh2024.com/wrapup).

## Heroku

Heroku is a hosting "platform as a service".
Heroku scales up and down to different amounts of compute power quite well and all costs are pro-rated (albeit by how long your app is set to that scale, not how much actual compute gets used).

Follow instructions on the [Heroku website](https://devcenter.heroku.com/articles/heroku-cli) to install the Heroku CLI and then create an app.
Mine is called `gph-site-test`.
Then, clone this repository and run `heroku git:remote -a gph-site-test`.
Deploy to Heroku with `git push heroku main`.

### Config Setup

We will need to configure Heroku. You can set environment variables using
`heroku config:set CONFIG_VAR=value`.

- **Buildpacks**: We use the following buildpacks.
  - [pgbouncer](https://github.com/heroku/heroku-buildpack-pgbouncer)
    - Optional, but can help with database connections.
  - [uv](https://github.com/dropseed/heroku-buildpack-uv)
    - [Hopefully, this becomes redundant soon](https://github.com/heroku/roadmap/issues/323)
  - heroku/python
- **Secrets**: Generally, variables are loaded from the environment. These include things like:
  - Secret key (MUST set to a securely random long string).
  - Discord API token (`DISCORD_TOKEN`), webhooks
  - Email credentials
  - Sentry URL
  - Database, Redis credentials (add-on credentials are managed by Heroku)
  - And so on.
- **Settings**:
  - The settings file is configured via an environment variable: `heroku config:set DJANGO_SETTINGS_MODULE=gph.settings.prod`

### Procfile

We need a `Procfile` to tell Heroku how to run our app. Ours has three lines:

- `release`: Run any pending migrations on new deploys.
- `web`: Run the webserver under pgbouncer, using gunicorn.
  - Settings in `gph/gunicorn.py`
- `worker`: Run a worker dyno to process e.g. Discord and email

### Resources

- [SQLite isn't a good fit for Heroku](https://devcenter.heroku.com/articles/sqlite3) because Heroku doesn't provide a "real" filesystem.
  - Fortunately Heroku provides easy-to-use PostgreSQL, so we need to switch Django to use that instead.
  - Running the prod website locally will be a bit harder because you need to get PostgreSQL running locally too.
- We install the `whitenoise` middleware so Django can serve static files directly in a production-ready way.

In theory, if you now visit `yourappname.herokuapp.com` you should see the properly styled front page of the puzzlehunt website with some text about a puzzlehunt. (Heroku will automatically run `collectstatic` and `migrate` for you.)

You will need to run `loaddata` manually: `heroku run python manage.py loaddata puzzles/fixtures/*`.

### Domains, Caching

If you want to use a custom domain, follow [Heroku's instructions](https://devcenter.heroku.com/articles/custom-domains).

We managed our DNS through Cloudflare, and used their caching as well.
We used a separate domain for caching static assets (pointed at the same dyno), though this is not strictly necessary.

Our cache rule was:

- URI Full, wildcard, `https://cdn.mitmh2024.com/static/*` OR
- URI Full, wildcard, `http://cdn.mitmh2024.com/static/*`

### Running the Heroku version locally

We have not tested these instructions, and just used `./manage.py runserver` each time.

The current codebase uses SQLite locally, and Heroku's database (Postgres) on prod.
The Django ORM layer slightly mitigates the risk of working on multiple databases, and we aren't doing anything super intensive or complex.

We've preserved instructions to Bring Your Own [PostgreSQL](https://www.postgresql.org/) Database and use it locally below.

#### One-time setup

You'll need to acquire [PostgreSQL](https://www.postgresql.org/) somehow (depending on your operating system) and make sure the server is running.
[Heroku](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup) has some docs.

You might need to create a Postgres user; it will be slightly easier for future tinkering if the username here is the same as your user account, but it doesn't have to be. You'll also want to create a Postgres database. To do those things, run `psql` as some user that already has an account and has create database permissions, most likely `postgres`. On Linux this is:

```shell
sudo -u postgres psql
```

Enter whichever of these two SQL commands you need into the `psql` prompt to create a new user with a password and a database. Fill in the values you want.

```psql
CREATE USER yourusername PASSWORD 'yourpassword';
CREATE DATABASE yourdbname;
```

Unless you've done something funky to explicitly allow other people to connect to your PostgreSQL server, this is only usable for local development and the password will be lying around in plaintext on your computer anyway, so the password doesn't have to be secure. But I haven't figured out how to not use one and have it work with later steps. After typing that and hitting Enter, if it worked, you can quit `psql` (maybe Ctrl-D).

Back in the `gph-site` directory, create a file called `.env` with these two lines, except in `DATABASE_URL`, replace the username, password, and database name with whatever you used above.

```shell
DATABASE_URL=postgres://yourusername:yourpassword@127.0.0.1:5432/yourdbname
DJANGO_SETTINGS_MODULE=gph.settings.dev
```

If you don't set the settings module, your local website might try to actually send emails or Discord notifications and such.

#### Every time

To set up other things (creating superusers, migrating or making migrations, loading data), you can mostly follow instructions in `README.md`, except that when asked to run `./manage.py something` you should instead run `heroku local:run ./manage.py something`. There is also one additional step because of Heroku's extra handling around static files: the first time you're running the website locally or any time you change the static assets, run `./manage.py collectstatic`.

After everything else is ready, to run the website, just run `heroku local`.
