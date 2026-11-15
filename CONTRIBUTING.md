# Contributing to MalaysiaCrime

These are the rules our group agreed on for changing this repository in WIF3005 Software Maintenance and Evolution. There are 8 of us pushing to one `master`, so everyone uses the same steps. That way the history shows who changed what and for which work package (WP), and WP8 can build the who-did-what table from it.

If you haven't set up the project yet, follow the [README](README.md) first.

## Summary

1. Update `master` on your computer.
2. Make a new branch for your WP from `master`.
3. Change the code, then run the app and the tests.
4. Commit with a message that starts with your WP number.
5. Push the branch and open a pull request (PR) into `master`.
6. One other member reviews and approves the PR.
7. Tan Yun Yu (`yy-y22`), who created our group's fork, merges it.

## 1. Update `master`

`master` is the main branch, and it should always run. Before you start working, get the newest version:

```bash
git checkout master
```

```bash
git pull origin master
```

## 2. Make a branch for your work

Don't commit straight to `master`. Make your own branch from it.

Name it `wp<number>-<short-description>`, in lowercase with hyphens. Some examples:

| WP | Example branch name |
| --- | --- |
| WP2 | `wp2-docs` |
| WP3 | `wp3-leaflet-migration` |
| WP5 | `wp5-csrf-security` |
| WP6 | `wp6-feed-tests` |

The first three are real branches in our repository. The commands below use `wp6-feed-tests` as the example.

```bash
git checkout -b wp6-feed-tests
```

`checkout -b` makes the branch and switches to it. To check which branch you're on, run `git branch`. The current one has a `*` next to it.

### If `master` changed while you were working

Other members will merge their PRs while you're still working, so your branch gets out of date. Before you open a PR, bring their changes into your branch:

```bash
git checkout master
```

```bash
git pull origin master
```

```bash
git checkout wp6-feed-tests
```

```bash
git merge master
```

If Git says there is a merge conflict, it means you and someone else changed the same lines. Open each file Git lists and keep the right lines. Delete the `<<<<<<<`, `=======` and `>>>>>>>` markers, then run `git add <file>` and `git commit`. If you're not sure which lines to keep, ask in the group chat.

## 3. Change the code and test it

- The code has to keep working on Python 2.7 and Django 1.3.1. Don't upgrade the packages in `requirements.txt` unless your WP is about that.
- Follow the style of the file you're editing. Python files use 4 spaces for indentation.
- Only change what your WP needs. If you find a different problem, open a GitHub Issue for it and fix it in a separate PR.
- If your change affects how to install, run or test the project, update [README.md](README.md) in the same PR. If it changes how the apps connect to each other, update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) too.

### Run the tests

Start the app first (see the [README](README.md)). Then open a second terminal in the project folder, set `SECRET_KEY` in it like the README shows, and run:

```bash
docker compose exec web python manage.py test crime main monitor
```

Right now there are 48 tests. 47 pass and 1 gives an error (`test_get_sitemap`), which we already know about (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code)). Your PR must not add any new failures or errors. If you add a feature or fix a bug, try to add a test for it as well.

Also open http://127.0.0.1:8000 and look at the pages you changed yourself.

## 4. Commit your changes

When you commit, Git saves your changes together with a message saying what you did.

### What not to commit

| Don't commit | Why |
| --- | --- |
| `settings.py` | Docker makes it from `settings_default.py`. It's in `.gitignore`. |
| `dev.db` | It's your local database, and Docker makes it. It's in `.gitignore`. |
| `*.pyc` | Python makes these files. They're in `.gitignore`. |
| Passwords, keys (including your `SECRET_KEY`), tokens | Anyone can read this repository. |
| Personal notes or tutorial answers | They aren't part of the project. |

If you want to keep a file only on your computer, add it to `.git/info/exclude`. It works like `.gitignore`, but it isn't shared with the group.

### Check, stage and commit

```bash
git status
```

```bash
git add README.md docs/ARCHITECTURE.md
```

```bash
git diff --staged
```

```bash
git commit -m "WP2: Add architecture overview with module diagram"
```

`git status` lists the files you changed. `git add <file>` picks the files for the next commit. Please name them one by one instead of using `git add .`, because that can add files you didn't mean to. `git diff --staged` shows exactly what will go into the commit, so read it before you commit.

### Commit message format

```text
WP<number>: <what the commit does>
```

- Start with your WP number and a colon.
- Then say what the commit does, starting with a verb like Add, Fix, Replace, Remove or Update.
- Keep the first line under about 72 characters.
- If the reason isn't clear from the first line, leave one empty line and explain it underneath.

Good examples:

```text
WP5: Load SECRET_KEY from environment variable
WP6: Fix southern edge check in send_all area filter
WP3: Replace Google Maps v2 with Leaflet on homepage
```

Bad examples: `update`, `fix bug`, `changes`, `final version 2`.

Keep commits small, one thing each. WP2 used one commit per document, for example, so the reviewer could check each file on its own.

## 5. Push and open a pull request

Send your branch to GitHub:

```bash
git push -u origin wp6-feed-tests
```

`-u` links your local branch to the one on GitHub, so after this you can just type `git push`.

Then open a pull request:

1. Go to https://github.com/yy-y22/malaysiacrime.
2. Click **Compare & pull request** next to your branch. If it isn't there, click **Pull requests** and then **New pull request**.
3. Check that base is `master` and compare is your branch.
4. Write the PR title in the same format as a commit message, for example `WP3: Replace Google Maps v2 with Leaflet`.
5. In the description, write what you changed and why, and link the Issue (for example `Closes #12`). Also say how you tested it: the test result and which pages you checked. If there's a part the reviewer should look at carefully, mention it.
6. Add one maintenance-type label (see [Labels](#labels)).
7. Pick a reviewer from the group under **Reviewers** on the right.

## 6. Review

Every PR needs 1 approval from a group member who didn't write it.

If you're the reviewer:

- Read the changed files in the **Files changed** tab.
- If you can, pull the branch and run the app and the tests yourself.
- Leave a comment on any line you think is wrong or unclear.
- Click **Review changes**, then **Approve** if it's ready, or **Request changes** if it isn't.

If you're the author, reply to every comment. To fix something, push new commits to the same branch and the PR updates by itself.

## 7. Merge

Only Tan Yun Yu (`yy-y22`) merges PRs into `master`. She created our group's fork, https://github.com/yy-y22/malaysiacrime, from the archived [Sinar/malaysiacrime](https://github.com/Sinar/malaysiacrime) repository. A PR gets merged once it has 1 approval and doesn't add any new test failures.

After the merge, delete your branch on GitHub (there's a **Delete branch** button on the PR page) and update your local `master` again like in step 1.

## Labels

Every Issue and PR gets one label for its type of maintenance. The names have to match the labels WP8 makes on GitHub.

| Label | Use it when the change... | Example from this project |
| --- | --- | --- |
| `Corrective` | fixes a bug or an error | Fix the area check in `send_all.py` |
| `Adaptive` | makes the system work in a new or changed environment | Replace the shut-down Google Maps API with Leaflet |
| `Perfective` | adds a feature, or makes the system faster or easier to use | Add pagination to the home page |
| `Preventive` | makes future maintenance easier or stops future problems | Write the README, add tests, set up CI |

If a change fits more than one type, pick the label for its main purpose and mention the others in the PR description.

## Continuous integration (CI)

GitHub doesn't run the tests automatically yet. WP6 is adding a GitHub Actions workflow for this. Until then, please run the tests on your own computer before you open a PR, and write the result in the PR description.

## Questions

Ask in the group chat, or open a GitHub Issue with your question.
