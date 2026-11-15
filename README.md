# MalaysiaCrime

<img src="static/images/logo.gif" alt="Malaysia Crime logo">

MalaysiaCrime is a website where people can report crimes on a map of Malaysia, comment on them, and get email alerts for an area they pick. It was built between 2009 and 2011 with Python 2.7 and Django 1.3.1.

Our group's repository, https://github.com/yy-y22/malaysiacrime, is a fork of [Sinar/malaysiacrime](https://github.com/Sinar/malaysiacrime), which is archived now. Sinar's copy was itself a fork of [zuLazman/malaysiacrime](https://github.com/zuLazman/malaysiacrime). We are 8 students maintaining it for WIF3005 Software Maintenance and Evolution at Universiti Malaya. We split the work into work packages (WP1 to WP8), and this README is part of WP2.

On the site you can:

- report a crime with a headline, date, place, details and a point on the map
- browse reports on the home page, by most recent update, or by most recent comment
- read the comments on a report (the original author turned off new comments in 2011)
- subscribe to an area of the map with your email and get an email when there is a new report there
- follow new reports through GeoRSS feeds, which are RSS feeds that also have the map position

About the map: WP3 and WP4 replaced the old Google map with Leaflet and OpenStreetMap on the home page, the report pages and the subscribe pages. The Commented and Recently updated pages still use Google Maps API v2. Google shut that API down, so the map on those two pages is empty, but the list of reports under it still works.

## Run it with Docker

Docker runs the project inside a small Linux container that already has Python 2.7 and the right package versions, so you don't need to install Python or Django yourself.

You need two things:

- [Git](https://git-scm.com/downloads). Check it with `git --version`.
- [Docker Desktop](https://www.docker.com/products/docker-desktop/). Open it and wait until the bottom-left corner says Engine running. Then check it with `docker compose version`.

Type the commands below in a terminal. On Windows you can use PowerShell or Command Prompt, and on macOS or Linux use Terminal.

### Steps

1. Download the code:

   ```bash
   git clone https://github.com/yy-y22/malaysiacrime.git
   ```

2. Go into the project folder:

   ```bash
   cd malaysiacrime
   ```

3. Set a secret key. Django uses it to sign cookies and other data, and the project won't start without it. You have to set it in every new terminal before any `docker compose` command, and that includes the second terminal you open for the tests. On your own computer any long random text is fine, and it can be different each time.

   In PowerShell:

   ```powershell
   $env:SECRET_KEY = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N")
   ```

   In Command Prompt:

   ```bat
   set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%
   ```

   On macOS or Linux:

   ```bash
   export SECRET_KEY="$(openssl rand -hex 32)"
   ```

   If you skip this, Docker stops with `required variable SECRET_KEY is missing a value`. Don't save your key in any file in the repository. WP5 added this step, and [MAINTENANCE_CSRF_SECURITY.md](MAINTENANCE_CSRF_SECURITY.md) explains why.

4. Build the container and start the website:

   ```bash
   docker compose up --build
   ```

   The first time takes a few minutes, because Docker has to download Python 2.7 and install the packages. It's ready when you see:

   ```text
   Development server is running at http://0.0.0.0:8000/
   Quit the server with CONTROL-C.
   ```

5. Open http://127.0.0.1:8000 in your browser. You should see the home page with a menu at the top and a map of Malaysia.

6. To stop it, go back to the terminal and press `Ctrl` + `C`.

After the first time, `docker compose up` without `--build` is enough. Only add `--build` again if someone changed `requirements.txt` or the `Dockerfile`.

If you already cloned the project before, get the newest code first with `git checkout master` and then `git pull origin master`.

### What happens when the container starts

Every time the container starts, the `Dockerfile`:

1. copies `settings_default.py` to `settings.py`, but only if `settings.py` doesn't exist yet
2. runs `python manage.py syncdb --noinput` and `python manage.py migrate`, which create the SQLite database file `dev.db` (or update its tables when someone adds a new migration)
3. starts the Django development server on port 8000

Your project folder is shared with the container. When you edit a template, just refresh the browser. When you edit a `.py` file, the server restarts by itself.

You will see `settings.py` and `dev.db` appear in your project folder. Both are in `.gitignore`, so Git won't commit them.

Because `settings.py` is only made when it's missing, it doesn't get later changes to `settings_default.py`. If `settings_default.py` changes, delete `settings.py` and start the container again.

### If you ran the project before WP5 was merged

WP5 changed `settings_default.py` on 15 November 2026. If your `settings.py` is older than that, CSRF protection is still off in it and it still has the old key written inside, so the test `test_create_view_uses_csrf_protection` fails. To fix it:

1. Stop the container with `docker compose down`.
2. Delete `settings.py` but keep `dev.db`. In PowerShell: `Remove-Item settings.py`. In Command Prompt: `del settings.py`. On macOS or Linux: `rm settings.py`.
3. Set `SECRET_KEY` and start the container again. Docker makes a new `settings.py`.

Be careful: the first start after WP5 also runs migration `0005`, which turns the edit passwords in your `dev.db` into hashes, and you can't undo that. If you want to keep your old database, copy `dev.db` somewhere else first.

### Add sample data (optional)

The database starts empty. To add 3 sample reports and 3 comments, start the website, open a second terminal in the project folder, and run:

```bash
docker compose exec web python manage.py loaddata main/fixtures/crimes.json main/fixtures/comments.json
```

It should print `Installed 6 object(s) from 2 fixture(s)`. Then open http://127.0.0.1:8000/recent/updated/ to see the reports.

The sample comments put the reports in the Commented list, but they don't show on the report pages. The comment file links them to the wrong type of object (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code)).

## Run the tests

Start the website first. Then open a second terminal, go to the project folder, set `SECRET_KEY` in it (step 3), and run:

```bash
docker compose exec web python manage.py test crime main monitor
```

`docker compose exec web` runs a command inside the running container, and this one tests the `crime`, `main` and `monitor` apps. Django makes a separate database for the tests, so your `dev.db` stays the same.

Right now the result looks like this (your time will be different):

```text
Ran 48 tests in 7.499s

FAILED (errors=1)
```

47 tests pass. The 1 error is `test_get_sitemap` (`TemplateDoesNotExist: sitemap.xml`). We already know about it, and it's in the list in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code).

We left `feeds` out of the command because it isn't in `INSTALLED_APPS`, so `manage.py test feeds` fails. Its only test checks that 1 + 1 = 2 anyway. WP6 will replace it with real tests.

## Useful commands

Run these from the project folder, after you set `SECRET_KEY` in that terminal.

| Command | What it does |
| --- | --- |
| `docker compose up --build` | Build the container and start the website. |
| `docker compose up -d` | Start the website in the background so you can keep using the terminal. |
| `docker compose logs -f web` | Show the server output. Press `Ctrl` + `C` to stop watching. |
| `docker compose down` | Stop and remove the container. Your code and `dev.db` stay. |
| `docker compose exec web python manage.py test crime main monitor` | Run the tests. |
| `docker compose exec web python manage.py shell` | Open a Python shell with the project loaded. |

### Start again with an empty database

1. Stop the container:

   ```bash
   docker compose down
   ```

2. Delete the database file. In PowerShell:

   ```powershell
   Remove-Item dev.db
   ```

   In Command Prompt:

   ```bat
   del dev.db
   ```

   On macOS or Linux:

   ```bash
   rm dev.db
   ```

3. Run `docker compose up` again. It makes a new, empty `dev.db`.

## Pages to try

| Address | Page |
| --- | --- |
| http://127.0.0.1:8000/ | Home page. The newest reports, 20 per page, in a list and on the map. |
| http://127.0.0.1:8000/crime/create/ | Report a crime. Move the map until the pin in the centre is on the right place. |
| http://127.0.0.1:8000/recent/updated/ | Recently updated reports (map is empty) |
| http://127.0.0.1:8000/recent/commented/ | Recently commented reports (map is empty) |
| http://127.0.0.1:8000/monitor/subscribe/ | Subscribe to an area (sending the form gives an error page, see below) |
| http://127.0.0.1:8000/feeds/latest.xml | GeoRSS feed of the newest reports |

## Known problems

- The map on the Commented and Recently updated pages is empty, because those two pages still use Google Maps API v2. No work package covers them yet.
- You can't post comments. The comment form on the report page is turned off in the template.
- http://127.0.0.1:8000/admin/ and http://127.0.0.1:8000/sitemap.xml show an error page (`TemplateDoesNotExist`).
- Sending the subscribe form shows an error page (`NameError`). The subscription still gets saved, but the confirmation email can't be sent because the container has no email server, and `monitor/views.py` is missing the import it needs to handle that error.
- Please don't put this version on the internet. WP5 fixed the CSRF, `SECRET_KEY` and password problems, but the site still runs on Django 1.3.1, which hasn't had security updates for years.

The full list, with file names and line numbers, is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code).

## Project layout

```text
malaysiacrime/
├── crime/                 # Crime model and report pages (create, show, edit)
├── main/                  # Home page, recent lists, about, search, sitemap
├── feeds/                 # GeoRSS feeds
├── monitor/               # Area subscriptions and the send_all email command
├── templates/             # HTML templates used by the running site
├── static/                # CSS, images and map icons
├── docs/                  # Architecture overview and diagram
├── wp7_evidence/          # Speed test results from WP7
├── MAINTENANCE_CSRF_SECURITY.md  # WP5 report: CSRF, SECRET_KEY, passwords
├── WP7_REPORT.md          # WP7 report: Commented list fix, 20 reports per page
├── settings_default.py    # Settings template (copied to settings.py)
├── urls.py                # Root URL routes
├── manage.py              # Django command-line tool
├── requirements.txt       # Django 1.3.1, South 0.7.3, Markdown 2.0.3
├── Dockerfile             # Python 2.7 image and start-up steps
└── docker-compose.yml     # Runs the "web" container on port 8000
```

If you want to know what each app does and how they connect, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Before you change anything, please read [CONTRIBUTING.md](CONTRIBUTING.md) for our rules on branches, commits, pull requests and labels.
