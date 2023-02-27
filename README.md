# 🌀 la-metro-dashboard

An Airflow-based dashboard for the LA Metro ETL pipeline!

## Running the app locally

### Requirements

- [Docker](https://hub.docker.com/search/?type=edition&offering=community)

### Getting started

Perform the following steps from your terminal.

1. Clone this repository and its submodule, then `cd` into the superproject.

    ```bash
    git clone --recursive https://github.com/Metro-Records/la-metro-dashboard.git
    cd la-metro-dashboard
    ```
2. Build `la-metro-dashboard` application, and create a local `.env` file. Fill
in the absolute location of your GPG keyring, usually the absolute path for ` ~/.gnupg`.

    ```bash
    docker-compose build
    cp .env.example .env
    # Fill in the correct value for GPG_KEYRING_PATH
    ```

3. Once the command exits, follow the instructions to build the [LA Metro Councilmatic application](https://github.com/Metro-Records/la-metro-councilmatic#setup)

4. In order to run the `la-metro-dashboard` application, the `la-metro-councilmatic`
app must already be running. Open a new shell, move into the `la-metro-councilmatic`
application, and run it.

	```bash
    cd la-metro-councilmatic && docker-compose up app
    ```

	Once la-metro-councilmatic is running, in your first shell, run the la-metro-dashboard application.

	```bash
	docker-compose up
	```

5. Finally, to visit the dashboard app, go to http://localhost:8080/admin/. The
Councilmatic app runs on http://localhost:8001/.

See the Airflow documentation for more on [navigating the UI](https://airflow.apache.org/docs/stable/ui.html)
and [development](https://airflow.apache.org/docs/stable/tutorial.html).

## Application dependencies

Dashboard DAGS are based on one of two applications:

- [`scrapers-lametro`](https://github.com/Metro-Records/scrapers-lametro/)
- [LA Metro Councilmatic](https://github.com/Metro-Records/la-metro-councilmatic)

The conversation on how to ensure DAGs are running against the current version
of these applications is captured [in this issue](https://github.com/Metro-Records/server-la-metro-dashboard/issues/1).

tl;dr - Application dependencies are packaged as Docker images and pushed to
GitHub Container Registry. When a task starts, it pulls the corresponding image,
runs a custom script to decrypt the bundled secrets and append dashboard-specific
connection strings, then executes its command in a container.

### Managing code

The dashboard runs DAGs from application images stored in GitHub Container
Registry:

- [`scrapers-us-municipal`](https://github.com/Metro-Records/scrapers-us-municipal/pkgs/container/scrapers-us-municipal)
- [LA Metro Councilmatic](https://github.com/Metro-Records/la-metro-councilmatic/pkgs/container/la-metro-councilmatic)

Both images are configured to build automatically from their corresponding
GitHub repositories. Commits to `master` (i.e., staging deployments) build a
`master` tag. Pushes to `deploy` (i.e., production deployments) build a `deploy`
tag.

### Managing secrets

When DAGs are run, [our custom Docker operator](operators/blackbox_docker_operator.py)
tries to decrypt the secrets bundled the application image using your local GPG keyring.
This does not seem to work for GPG keys with a passphrase, i.e., your personal
GPG key. If decryption fails, the dashboard will fall back to using the example
settings files. (See [`scripts/concat_settings.sh`](scripts/concat_settings.sh).)

#### `scrapers-us-municipal`

Scrapes will run with the default settings file. **Note that running the bill
scrape without the encrypted token will not capture private bills,** however it
should provide enough signal to test whether scrapes are working unless you are
specifically trying to test private bill logic.

#### LA Metro Councilmatic

Metro processing requires AWS credentials and a SmartLogic API token, i.e.,
**Metro DAGs will fail locally without decrypted secrets.**

If you need to test the Metro ETL pipeline, I would suggest manually deploying
your branch to staging and running the DAGs there, as the server has the
appropriate keys to decrypt Metro application secrets.

If you must work locally, you can follow steps 1-5 in our instructions for
[moving keys between servers](https://github.com/datamade/how-to/blob/master/shell/moving-keys-between-servers.md)
to export the private key, then log out of the server and `scp` it down to your
computer:

```bash
# pubkey.txt is a misnomer from the linked documentation – this is a text file
# containing the *private* key you exported using gpg --export-secret-key
scp ubuntu@lametro-upgrade.datamade.us:/home/ubuntu/pubkey.txt .
gpg --import pubkey.txt
```

Don't forget to remove `pubkey.txt` from the server and from your local machine
after you've imported the keys successfully.

Now you can run Metro DAGs locally using decrypted secrets.

### Adding users

Admins can add users on the 'List Users' page located in the 'Security' dropdown on
the top Airflow toolbar. Each user is assigned a role, which has associated permissions.
The Airflow documentation has a thorough explanation of 
[permissions](https://airflow.apache.org/docs/apache-airflow/stable/security/access-control.html).
The role 'Metro Admin' grants users access only to the Dashboard view.
