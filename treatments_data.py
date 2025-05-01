import requests
import json
from prefect import task,flow
@task(task_run_name="Fetch_data_for_treatements")
def Fetch_data_for_treatments():
    url = "https://924f-105-73-96-18.ngrok-free.app/treatments"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()  # Convert response to Python dict/list
        print("Received data:", data)

        # Save to a JSON file
        with open("treatments_data.json", "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)  # indent for readability

        print("Data successfully saved to 'patients_data.json'")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        
@flow
def treatments_data_flow():
    raw_data = Fetch_data_for_treatments()

    # You can add more tasks here that process raw_data
    print("Flow completed.")

if __name__ == "__main__":
    treatments_data_flow()
   