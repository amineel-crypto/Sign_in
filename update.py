from prefect import task, flow
import requests
import json
from datetime import timedelta

# URLs source
URLS = {
    "patients": "https://924f-105-73-96-18.ngrok-free.app/patients",
    "diagnoses": "https://924f-105-73-96-18.ngrok-free.app/diagnoses",
    "treatments": "https://924f-105-73-96-18.ngrok-free.app/treatments"
}

@task(task_run_name="Download {name}")
def download_data(name, url):
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"data/{name}.json", "w") as f:
            json.dump(response.json(), f, indent=4)
        print(f"Data saved to data/{name}.json")
    else:
        raise Exception(f"Failed to fetch {name} from {url}")

@flow(name="Update Healthcare Data")
def update_data_flow():
    for name, url in URLS.items():
        download_data(name, url)

if __name__ == "__main__":
    update_data_flow.serve(
        name="hourly_update",
        interval=timedelta(hours=1),  # Ou utiliser cron="0 * * * *"
        tags=["healthcare", "data-update"],
        description="Mise à jour horaire des données patients, diagnostics et traitements"
    )