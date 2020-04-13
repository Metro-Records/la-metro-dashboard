# la-metro-dashboard
An Airflow-based dashboard for LA Metro

## Running the app locally

### Requirements

- [Docker](https://hub.docker.com/search/?type=edition&offering=community)

### Getting started

Perform the following steps from your terminal.

1. Clone this repository and its submodule, then `cd` into the superproject.

    ```bash
    git clone --recursive https://github.com/datamade/la-metro-dashboard.git
    cd la-metro-dashboard
    ```
2. Build and run the la-metro-dashboard applicaton.

    ```bash
    docker-compose build
    ```

3. Once the command exits, follow the instructions to build the [LA Metro Councilmatic application](https://github.com/datamade/la-metro-councilmatic#setup)

4. In order to run the la-metro-dashboard application, the la-metro-councilmatic app must already be running. Open a new shell, move into the la-metro-councilmatic application, and run it. 

	```bash
    cd la-metro-councilmatic && docker-compose up app
    ``` 

	Once la-metro-councilmatic is running, in your first shell, run the la-metro-dashboard application.

	```bash
	docker-compose up
	```

5. Finally, to visit the dashboard app, go to http://localhost:8080/admin/. The councilmatic app runs on http://localhost:8000/.
