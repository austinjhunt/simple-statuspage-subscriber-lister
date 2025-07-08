# get_subscribers_for_component.py
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

SUBSCRIBER_FIELDS_TO_PRINT = [
    "id",
    "email",
    "created_at",
    "mode",
    "phone_number",
]

STATUSPAGE_TOKEN = os.getenv("STATUSPAGE_TOKEN")
STATUSPAGE_PAGE_ID = os.getenv("STATUSPAGE_PAGE_ID")
BASE_URI = f"https://api.statuspage.io/v1/pages/{STATUSPAGE_PAGE_ID}"


def get_component_id_from_name(component_name):
    logger.info({"function": "get_component_id_from_name", "component_name": component_name})
    url = f"{BASE_URI}/components"
    headers = {"Authorization": f"OAuth {STATUSPAGE_TOKEN}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    for component in response.json():
        if component["name"].lower() == component_name.lower():
            return component["id"]

    raise ValueError(f"Component '{component_name}' not found.")


def get_all_subscribers():
    """Paginate through all subscribers (starting at page 0)."""
    url = f"{BASE_URI}/subscribers"
    headers = {"Authorization": f"OAuth {STATUSPAGE_TOKEN}"}
    subscribers = []
    page = 0

    while True:
        params = {"page": page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        subscribers.extend(data)
        page += 1

    return subscribers


def get_subscribers_for_component(component_id):
    logger.info({"function": "get_subscribers_for_component", "component_id": component_id})
    all_subscribers = get_all_subscribers()

    component_subscribers = [
        {field: sub.get(field) for field in SUBSCRIBER_FIELDS_TO_PRINT}
        for sub in all_subscribers
        if component_id in sub.get("components", [])
    ]

    logger.info(
        {
            "function": "get_subscribers_for_component",
            "component_id": component_id,
            "component_subscribers_count": len(component_subscribers),
        }
    )

    return component_subscribers


def save_to_csv(filename, data):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUBSCRIBER_FIELDS_TO_PRINT)
        writer.writeheader()
        writer.writerows(data)
    logger.info({"message": f"Subscribers saved to CSV file: {filename}"})


def save_to_json(filename, data):
    with open(filename, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info({"message": f"Subscribers saved to JSON file: {filename}"})


def main(component_name=None, component_id=None, out_csv=None, out_json=None):
    try:
        if component_name and not component_id:
            component_id = get_component_id_from_name(component_name)

        subscribers = get_subscribers_for_component(component_id)

        if not subscribers:
            logger.info(
                {
                    "function": "main",
                    "message": "No subscribers found.",
                    "component_id": component_id,
                }
            )
            return

        if out_csv:
            save_to_csv(out_csv, subscribers)

        if out_json:
            save_to_json(out_json, subscribers)

        logger.info(
            {
                "function": "main",
                "subscribers_count": len(subscribers),
                "component_id": component_id,
            }
        )
        for subscriber in subscribers:
            logger.info(subscriber)

    except Exception as e:
        logger.error(
            {
                "function": "main",
                "error": str(e),
                "component_name": component_name,
                "component_id": component_id,
            }
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Statuspage subscribers for a component.")
    parser.add_argument("--component-name", type=str, help="Name of the component.")
    parser.add_argument("--component-id", type=str, help="ID of the component.")
    parser.add_argument("--out-csv", type=str, help="Path to output CSV.")
    parser.add_argument("--out-json", type=str, help="Path to output JSON.")
    args = parser.parse_args()

    if not args.component_name and not args.component_id:
        parser.error("You must provide either --component-name or --component-id.")

    main(
        component_name=args.component_name,
        component_id=args.component_id,
        out_csv=args.out_csv,
        out_json=args.out_json,
    )
