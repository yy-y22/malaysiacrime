<div align="center">

<img src="static/images/logo.gif" alt="Malaysia Crime logo">

# MalaysiaCrime

A website where people report crimes on a map of Malaysia, comment on them, and get email alerts for an area they choose.

[Run it](#run-it-with-docker) | [Run the tests](#run-the-tests) | [How the code is organised](docs/ARCHITECTURE.md) | [Contributing](CONTRIBUTING.md)

</div>

MalaysiaCrime was built between 2009 and 2011 with Python 2.7 and Django 1.3.1. Our group's repository, https://github.com/yy-y22/malaysiacrime, is a fork of [Sinar/malaysiacrime](https://github.com/Sinar/malaysiacrime), which is archived now (Sinar's copy was itself a fork of [zuLazman/malaysiacrime](https://github.com/zuLazman/malaysiacrime)). We are a group of 8 students maintaining it for the WIF3005 Software Maintenance and Evolution course at Universiti Malaya.

The site lets people:

- report a crime with a headline, date, place, details and a point on the map
- browse reports on the home page, by most recent update, or by most recent comment
- read the comments on a report (the original author turned off posting new comments in 2011)
- subscribe to an area of the map with an email address, and get an email about new reports there
- follow new reports through GeoRSS feeds (RSS feeds that also include the map position)

> [!WARNING]
> The map does not work yet. The site uses Google Maps API v2, which Google has shut down, so the map area is empty. The map is also what fills in the position for the report, edit and subscribe forms, so these forms cannot be sent from the browser. The pages still load. Work packages 3 and 4 will replace the map with Leaflet and OpenStreetMap.

## Run it with Docker

Docker runs the project inside a small Linux "container" that already has Python 2.7 and the correct package versions. You do not need to install Python or Django on your computer.

### What you need

| Tool | How to check it works |
| --- | --- |
| [Git](https://git-scm.com/downloads) | `git --version` prints a version number. |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Open Docker Desktop. The bottom-left corner says **Engine running**. `docker compose version` prints a version number. |

Type the commands below in a terminal. On Windows you can use PowerShell or Command Prompt. On macOS or Linux, use Terminal.

### Steps

1. Download the code:

   ```bash
   git clone https://github.com/yy-y22/malaysiacrime.git
   ```

2. Go into the project folder:

   ```bash
   cd malaysiacrime
   ```

3. Build the container and start the website:

   ```bash
   docker compose up --build
   ```

   The first time takes a few minutes because Docker has to download Python 2.7 and install the packages. It is ready when the terminal shows:

   ```text
   Development server is running at http://0.0.0.0:8000/
   Quit the server with CONTROL-C.
   ```

4. Open http://127.0.0.1:8000 in your browser. You should see the MalaysiaCrime home page with a menu at the top.

5. To stop the website, go back to the terminal and press `Ctrl` + `C`.

After the first time, `docker compose up` (without `--build`) is enough. Use `--build` again if someone changed `requirements.txt` or the `Dockerfile`.

If you cloned the project before, get the newest code first with `git checkout master` and then `git pull origin master`.

### What happens when the container starts

Every time the container starts, the `Dockerfile` does these steps:

1. Copies `settings_default.py` to `settings.py`, but only if `settings.py` does not exist yet.
2. Runs `python manage.py syncdb --noinput` and `python manage.py migrate`. These create the SQLite database file `dev.db`.
3. Starts the Django development server on port 8000.

The project folder on your computer is shared with the container. If you edit a template, just refresh the browser. If you edit a `.py` file, the server restarts by itself.

`settings.py` and `dev.db` appear in your project folder. Both are in `.gitignore`, so Git will not commit them.

Note: because `settings.py` is only created when it is missing, it will not pick up later changes to `settings_default.py`. If `settings_default.py` changes, delete `settings.py` and start the container again.

### Add sample data (optional)

The database is empty at the start. To add 3 sample reports and 3 comments, start the website, open a second terminal in the project folder, and run:

```bash
docker compose exec web python manage.py loaddata main/fixtures/crimes.json main/fixtures/comments.json
```

It should print `Installed 6 object(s) from 2 fixture(s)`. Then open http://127.0.0.1:8000/recent/updated/ to see the reports.

The sample comments put the reports in the **Commented** list, but you will not see them on the report pages. This is because the comment file links them to the wrong type of object (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code)).

## Run the tests

Start the website first (see above). Then open a second terminal, go to the project folder, and run:

```bash
docker compose exec web python manage.py test crime main monitor
```

`docker compose exec web` runs a command inside the running container. This command tests the `crime`, `main` and `monitor` apps. Django makes a separate test database for the tests, so the data in your `dev.db` does not change.

At the moment the result looks like this:

```text
Ran 24 tests in 3.155s

FAILED (errors=1)
```

23 tests pass. The 1 error is `test_get_sitemap` (`TemplateDoesNotExist: sitemap.xml`). We already know about it, and it is listed in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code). The time will be different on your computer.

We left `feeds` out of the command because it is not in `INSTALLED_APPS`, so `manage.py test feeds` fails. Its only test checks that 1 + 1 = 2 anyway. Work package 6 will replace it with real tests.

## Useful commands

Run these from the project folder.

| Command | What it does |
| --- | --- |
| `docker compose up --build` | Build the container and start the website. |
| `docker compose up -d` | Start the website in the background, so you can keep using the terminal. |
| `docker compose logs -f web` | Show the server output. Press `Ctrl` + `C` to stop watching. |
| `docker compose down` | Stop and remove the container. Your code and `dev.db` are kept. |
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

3. Start the website again with `docker compose up`. It creates a new, empty `dev.db`.

## Pages to try

| Address | Page |
| --- | --- |
| http://127.0.0.1:8000/ | Home page |
| http://127.0.0.1:8000/crime/create/ | Report a crime form (it opens, but cannot be sent without the map) |
| http://127.0.0.1:8000/recent/updated/ | Recently updated reports |
| http://127.0.0.1:8000/recent/commented/ | Recently commented reports |
| http://127.0.0.1:8000/monitor/subscribe/ | Subscribe to an area |
| http://127.0.0.1:8000/feeds/latest.xml | GeoRSS feed of the newest reports |

## Known problems

- The map is empty because Google Maps API v2 is shut down. Without it, the report, edit and subscribe forms cannot be sent from the browser.
- Visitors cannot post comments. The comment form on the report page is turned off in the template.
- http://127.0.0.1:8000/admin/ and http://127.0.0.1:8000/sitemap.xml show an error page (`TemplateDoesNotExist`).
- If the subscribe form does get sent (for example by a test or a script), the site shows an error page (`NameError`). The container has no email server, and `monitor/views.py` is missing the import it needs to handle that case.
- The security settings are not safe for a public server. CSRF protection is off, `SECRET_KEY` is a placeholder in `settings_default.py`, and report edit passwords are saved as plain text. Work package 5 is fixing these, so please do not put this version on the internet.

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
├── settings_default.py    # Settings template (copied to settings.py)
├── urls.py                # Root URL routes
├── manage.py              # Django command-line tool
├── requirements.txt       # Django 1.3.1, South 0.7.3, Markdown 2.0.3
├── Dockerfile             # Python 2.7 image and start-up steps
└── docker-compose.yml     # Runs the "web" container on port 8000
```

To understand what each app does and how they connect, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Before you change anything, please read [CONTRIBUTING.md](CONTRIBUTING.md) for our rules on branches, commits, pull requests and labels.
