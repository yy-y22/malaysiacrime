# Contributing to MalaysiaCrime

This file has the rules our group of 8 follows when we change this repository for WIF3005 Software Maintenance and Evolution. We all follow the same steps, so that it is easy to see who changed what and in which work package (WP).

If you have not set up the project yet, follow the [README](README.md) first.

## Summary

1. Update `master` on your computer.
2. Make a new branch for your WP from `master`.
3. Change the code, then run the app and the tests.
4. Commit with a message that starts with your WP number.
5. Push the branch and open a pull request (PR) into `master`.
6. One other member reviews and approves the PR.
7. Tan Yun Yu (`yy-y22`), who created our group's fork, merges it.

Each step is explained below.

## 1. Update `master`

`master` is the main branch and it should always run. Before you start any work, get the newest version:

```bash
git checkout master
```

```bash
git pull origin master
```

## 2. Make a branch for your work

Do not commit directly to `master`. Make your own branch from it.

Name the branch `wp<number>-<short-description>`, using lowercase letters and hyphens. For example:

| WP | Example branch name |
| --- | --- |
| WP2 | `wp2-docs` |
| WP3 | `wp3-leaflet-homepage` |
| WP6 | `wp6-feed-tests` |

```bash
git checkout -b wp3-leaflet-homepage
```

`checkout -b` creates the branch and switches to it. To see which branch you are on, run `git branch`. The current branch has a `*` next to it.

### If `master` changed while you were working

Other members will merge their PRs while you are still working, so your branch gets out of date. Before you open a PR, bring their changes into your branch:

```bash
git checkout master
```

```bash
git pull origin master
```

```bash
git checkout wp3-leaflet-homepage
```

```bash
git merge master
```

If Git says there is a merge conflict, it means you and another member changed the same lines. Open each file that Git lists and keep the correct lines. Delete the `<<<<<<<`, `=======` and `>>>>>>>` markers, then run `git add <file>` and `git commit`. If you are not sure which lines to keep, ask in the group chat.

## 3. Change the code and test it

- The code must keep working on Python 2.7 and Django 1.3.1. Do not upgrade the packages in `requirements.txt` unless that is what your WP is about.
- Follow the style of the file you are editing. Python files use 4 spaces for indentation.
- Only change what your WP needs. If you find a different problem, open a GitHub Issue for it and fix it in a separate PR.
- If your change affects how to install, run or test the project, update [README.md](README.md) in the same PR. If it changes how the apps connect to each other, update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) as well.

### Run the tests

Start the app first (see the [README](README.md)). Then, in a second terminal in the project folder, run:

```bash
docker compose exec web python manage.py test crime main monitor
```

Right now there are 24 tests: 23 pass and 1 gives an error (`test_get_sitemap`). We already know about that error; see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#things-to-know-before-you-change-code). Your PR must not add any new failures or errors. If you add a feature or fix a bug, try to add a test for it too.

Also open http://127.0.0.1:8000 and check the pages you changed yourself.

## 4. Commit your changes

A commit is a saved snapshot of your changes, together with a message that describes them.

### What not to commit

| Do not commit | Why |
| --- | --- |
| `settings.py` | Docker creates it from `settings_default.py`. It is in `.gitignore`. |
| `dev.db` | This is your local database. Docker creates it. It is in `.gitignore`. |
| `*.pyc` | Python creates these files. They are in `.gitignore`. |
| Passwords, keys, tokens | Anyone can read this repository. |
| Personal notes or tutorial answers | They are not part of the project. |

If you want to keep a file on your computer only, add it to `.git/info/exclude`. It works the same way as `.gitignore`, but it is not shared with the group.

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

`git status` lists the files you changed. `git add <file>` picks which files go into the next commit. Please name the files one by one and avoid `git add .`, because it can add files you did not mean to add. `git diff --staged` shows exactly what will be committed, so read it before you commit.

### Commit message format

```text
WP<number>: <what the commit does>
```

- Start with your WP number and a colon.
- Then write what the commit does, starting with a verb such as Add, Fix, Replace, Remove or Update.
- Keep the first line shorter than about 72 characters.
- If the reason for the change is not clear from the first line, leave one empty line and explain it below.

Good examples:

```text
WP5: Load SECRET_KEY from environment variable
WP6: Fix southern edge check in send_all area filter
WP3: Replace Google Maps v2 with Leaflet on homepage
```

Bad examples: `update`, `fix bug`, `changes`, `final version 2`.

Try to make small commits that each do one thing. They are much easier to review than one big commit.

## 5. Push and open a pull request

Send your branch to GitHub:

```bash
git push -u origin wp3-leaflet-homepage
```

`-u` links your local branch to the branch on GitHub. After this, `git push` on its own is enough.

Then open a pull request:

1. Go to https://github.com/yy-y22/malaysiacrime.
2. Click **Compare & pull request** next to your branch. If you do not see it, click **Pull requests** and then **New pull request**.
3. Check that **base** is `master` and **compare** is your branch.
4. Write the PR title in the same format as a commit message, for example `WP3: Replace Google Maps v2 with Leaflet`.
5. In the description, write what you changed and why, and link the Issue (for example `Closes #12`). Also write how you tested it: the test result and the pages you checked. If there is a part the reviewer should look at carefully, mention it.
6. Add one maintenance-type label (see [Labels](#labels)).
7. Choose a reviewer from the group under **Reviewers** on the right side.

## 6. Review

Every PR needs 1 approval from a group member who did not write it.

If you are the reviewer:

- Read the changed files in the **Files changed** tab.
- If you can, pull the branch and run the app and the tests yourself.
- Leave a comment on any line that you think is wrong or unclear.
- Click **Review changes**, then **Approve** if it is ready, or **Request changes** if it is not.

If you are the author, reply to every comment. To fix something, push new commits to the same branch and the PR will update automatically.

## 7. Merge

Only Tan Yun Yu (`yy-y22`) merges PRs into `master`. She created our group's fork, https://github.com/yy-y22/malaysiacrime, from the archived [Sinar/malaysiacrime](https://github.com/Sinar/malaysiacrime) repository. A PR is merged after it has 1 approval and does not add any new test failures.

After the merge, delete your branch on GitHub (the PR page has a **Delete branch** button) and update your local `master` again as in step 1.

## Labels

Every Issue and PR gets one label for its type of maintenance. These names have to match the labels that WP8 creates on GitHub.

| Label | Use it when the change... | Example from this project |
| --- | --- | --- |
| `Corrective` | fixes a bug or an error | Fix the area check in `send_all.py` |
| `Adaptive` | makes the system work in a new or changed environment | Replace the shut-down Google Maps API with Leaflet |
| `Perfective` | adds a feature, or makes the system faster or easier to use | Add pagination to the home page |
| `Preventive` | makes future maintenance easier or stops future problems | Write the README, add tests, set up CI |

If a change fits more than one type, choose the label for its main purpose and mention the other types in the PR description.

## Continuous integration (CI)

GitHub does not run the tests automatically yet. WP6 is adding a GitHub Actions workflow for this. Until it is ready, please run the tests on your own computer before you open a PR and write the result in the PR description.

## Questions

Ask in the group chat, or open a GitHub Issue with your question.
