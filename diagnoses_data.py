import requests
import json
from prefect import task,flow

url = "https://924f-105-73-96-18.ngrok-free.app/diagnoses"
@task(task_run_name="diagnoses_data_fetch")
def fetch_diag_data():
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()  # Convert response to Python dict/list
        print("Received data:", data)

        # Save to a JSON file
        with open("diagnoses_data.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)  # indent for readability

        print("Data successfully saved to 'patients_data.json'")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

@flow
def treatments_data_flow():
    raw_data = fetch_diag_data()

    # You can add more tasks here that process raw_data
    print("Flow completed.")

if __name__ == "__main__":
    treatments_data_flow()
   