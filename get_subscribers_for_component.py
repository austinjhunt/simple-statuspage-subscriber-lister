# get_subscribers_for_component.py
# This script retrieves the subscribers for a specific component from the Atlassian Statuspage API.
# The API itself does not have an endpoint to directly fetch subscribers for a component, but we can retrieve subscribers and then filter out those subscribed to a given component.

import requests
import csv
import json
import argparse
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Once matched, these fields will be printed for each subscriber
SUBSCRIBER_FIELDS_TO_PRINT = [
    "id",
    "email",
    "created_at",
    "mode",
    "phone_number",
]

STATUSPAGE_TOKEN = os.getenv("STATUSPAGE_TOKEN")
STATUSPAGE_PAGE_ID = os.getenv("STATUSPAGE_PAGE_ID")

base_uri = f"https://api.statuspage.io/v1/pages/{STATUSPAGE_PAGE_ID}/"  # Base URI specific to our statuspage instance


def get_component_id_from_name(component_name):
    """Retrieve the component ID from its name."""
    logger.info(
        {
            "function": "get_component_id_from_name",
            "component_name": component_name,
            "base_uri": base_uri,
        }
    )
    url = f"{base_uri}/components"
    headers = {"Authorization": f"OAuth {STATUSPAGE_TOKEN}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve components: {response.status_code} - {response.text}")
    components = response.json()
    for component in components:
        if component["name"].lower() == component_name.lower():
            return component["id"]
    raise ValueError(f"Component '{component_name}' not found.")


def get_subscribers_for_component(component_id):
    """Retrieve subscribers for a specific component."""
    logger.info(
        {
            "function": "get_subscribers_for_component",
            "component_id": component_id,
            "base_uri": base_uri,
        }
    )
    url = f"{base_uri}/subscribers"
    headers = {"Authorization": f"OAuth {STATUSPAGE_TOKEN}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve subscribers: {response.status_code} - {response.text}")

    subscribers = response.json()
    component_subscribers = []
    for subscriber in subscribers:
        # Check if the subscriber is subscribed to the specific component
        if "components" in subscriber:
            for cid in subscriber["components"]:
                if cid == component_id:

                    # If the subscriber is subscribed to the component, add them to the list
                    # We will only keep the fields we want to print
                    component_subscriber = {
                        field: subscriber.get(field) for field in SUBSCRIBER_FIELDS_TO_PRINT
                    }
                    component_subscribers.append(component_subscriber)
                    break

    logger.info(
        {
            "function": "get_subscribers_for_component",
            "component_id": component_id,
            "component_subscribers_count": len(component_subscribers),
        }
    )

    return component_subscribers


def main(component_name=None, component_id=None, out_csv=None, out_json=None):
    """Main function to get subscribers for a specific component.

    Args:
        component_name (str): Name of the component to retrieve subscribers for.
        component_id (str): ID of the component to retrieve subscribers for.
        out_csv (str): Output CSV file to save the subscribers (optional).
        out_json (str): Output JSON file to save the subscribers (optional).

    Raises:
        Exception: If there is an error retrieving subscribers or components.
    """
    logger.info(
        {
            "function": "main",
            "component_name": component_name,
            "component_id": component_id,
            "out_csv": out_csv,
            "out_json": out_json,
        }
    )
    try:
        if component_name and not component_id:
            component_id = get_component_id_from_name(component_name)
        subscribers = get_subscribers_for_component(component_id)
        if out_csv:
            # Write subscribers to CSV file
            with open(out_csv, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=SUBSCRIBER_FIELDS_TO_PRINT)
                writer.writeheader()
                writer.writerows(subscribers)
            logger.info(
                {
                    "function": "main",
                    "message": f"Subscribers saved to CSV file: {out_csv}",
                }
            )
        if out_json:
            # Write subscribers to JSON file
            with open(out_json, mode="w", encoding="utf-8") as jsonfile:
                json.dump(subscribers, jsonfile, indent=4)
            logger.info(
                {
                    "function": "main",
                    "message": f"Subscribers saved to JSON file: {out_json}",
                }
            )

        if not subscribers:
            logger.info(
                {
                    "function": "main",
                    "message": "No subscribers found for the specified component.",
                    "component_name": component_name,
                    "component_id": component_id,
                    "out_csv": out_csv,
                    "out_json": out_json,
                }
            )
        else:
            logger.info(
                logger.info(
                    {
                        "function": "main",
                        "component_name": component_name,
                        "component_id": component_id,
                        "subscribers_count": len(subscribers),
                    }
                )
            )
            for subscriber in subscribers:
                logger.info(subscriber)  # Print the full subscriber object
    except Exception as e:
        logger.error(
            {
                "function": "main",
                "error": str(e),
                "component_name": component_name,
                "component_id": component_id,
                "out_csv": out_csv,
                "out_json": out_json,
            }
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get subscribers for a specific component (by either component ID or component name) from Atlassian Statuspage."
    )
    parser.add_argument(
        "--component-name", type=str, help="Name of the component to retrieve subscribers for."
    )
    parser.add_argument(
        "--out-csv", type=str, help="Output CSV file to save the subscribers (optional)."
    )
    parser.add_argument(
        "--out-json", type=str, help="Output JSON file to save the subscribers (optional)."
    )
    parser.add_argument(
        "--component-id",
        type=str,
        help="ID of the component to retrieve subscribers for (optional).",
    )
    args = parser.parse_args()

    if not args.component_name and not args.component_id:
        parser.error("At least one of --component-name or --component-id must be provided.")

    if args.component_id:
        main(component_id=args.component_id, out_csv=args.out_csv, out_json=args.out_json)
    else:
        main(component_name=args.component_name, out_csv=args.out_csv, out_json=args.out_json)
