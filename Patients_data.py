import requests
import json
from prefect import task, flow

@task(task_run_name="Fetch_data_of_patients")
def fetch_data_of_patients():
    url = "https://924f-105-73-96-18.ngrok-free.app/patients"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses

        data = response.json()
        print("Received data:", data)

        # Save to JSON file
        with open("patients_data.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)

        print("Data successfully saved to 'patients_data.json'")

        return data  # Return data for use in downstream tasks

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise  # Prefect will catch and mark task as failed
    
@flow
def patients_data_flow():
    raw_data = fetch_data_of_patients()

    # You can add more tasks here that process raw_data
    print("Flow completed.")

if __name__ == "__main__":
    patients_data_flow()