from dotenv import load_dotenv
import os
import requests
import random
from datetime import datetime, timedelta
import pprint

class FlightSearch:
    def __init__(self):
        load_dotenv()
        self.dead_places = 0
        self.api_key = os.getenv("amadeus_api_key")
        self.api_secret = os.getenv("amadeus_api_secret")
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.location_url = "https://test.api.amadeus.com/v1/reference-data/locations"
        self.search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        self.token = self._get_token()

    def _get_token(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.api_secret
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_iata_code(self, city_name):
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"keyword": city_name, "subType": "CITY"}
        response = requests.get(self.location_url, headers=headers, params=params)
        response.raise_for_status()
        try:
            return response.json()["data"][0]["iataCode"]
        except (KeyError, IndexError):
            self.dead_places += 1
            print(f"❌ Could not find IATA code for: {city_name}")
            return ""

    def get_monthly_dates(self, start_date, months=6, day=15):
        dates = []
        year = start_date.year
        month = start_date.month

        for _ in range(months):
            if month > 12:
                month -= 12
                year += 1

            # Try to create the date for the chosen day in this month
            try:
                date = datetime(year, month, day)
            except ValueError:
                # If day does not exist in the month (e.g., Feb 30), use last day of the month
                if month == 12:
                    next_month = datetime(year + 1, 1, 1)
                else:
                    next_month = datetime(year, month + 1, 1)
                date = next_month - timedelta(days=1)

            if date >= start_date:
                dates.append(date)

            month += 1

        return dates

    def get_flights(self, city_data):
        start_date = datetime.today() + timedelta(days=14)
        months_ahead = 6
        children = input("Step Two: Please enter the number of children you have:")
        adults = input("Step Three: Please enter the number of adults you have:")
        flight_details = input(
            "Step Four: Please enter if you want this flight to be:\n"
            "nonstop   multi-leg   both \n"
        ).strip().lower()

        # Generate one date per month (15th of each month)
        search_dates = []
        for i in range(months_ahead):
            year = (start_date.month + i - 1) // 12 + start_date.year
            month = (start_date.month + i - 1) % 12 + 1
            try:
                date = datetime(year, month, 15)
            except ValueError:
                # Use last day of month if 15th invalid
                if month == 12:
                    next_month = datetime(year + 1, 1, 1)
                else:
                    next_month = datetime(year, month + 1, 1)
                date = next_month - timedelta(days=1)
            search_dates.append(date)

        if flight_details not in ["nonstop", "multi-leg", "both"]:
            print("Sorry, invalid choice. Please retry.")
            return  # or loop again if you want

        for city_id in city_data:
            data = city_data[city_id]
            city = data['city']
            iata = data['iataCode']
            low_price = data['lowestPrice']

            print(f"\n✈️ Searching for {flight_details} flights to {city} ({iata}) over the next 6 months:")

            for departure_date in search_dates:
                formatted_date = departure_date.strftime("%Y-%m-%d")
                print(f"\n🔍 Checking {formatted_date}")

                headers = {'Authorization': f'Bearer {self.token}'}
                params = {
                    'originLocationCode': 'LAX',
                    'destinationLocationCode': iata,
                    'departureDate': formatted_date,
                    'adults': adults,
                    'children': children,
                    'travelClass': 'ECONOMY',
                    'currencyCode': 'USD',
                    'max': 5 if flight_details != 'nonstop' else 1
                }
                # Add nonStop param only if searching nonstop flights exclusively
                if flight_details == "nonstop":
                    params['nonStop'] = 'true'

                try:
                    response = requests.get(self.search_url, headers=headers, params=params)
                    response.raise_for_status()
                    flights = response.json()

                    if not flights.get("data"):
                        print(f"No flights data returned for {formatted_date} to {city}.")
                        continue

                    found_deal = False
                    for flight_offer in flights["data"]:
                        price_info = flight_offer["price"]
                        total_price = float(price_info["total"])
                        currency = price_info["currency"]

                        # Filter logic by flight_details type:
                        if flight_details == "nonstop":
                            # All offers here are nonstop (due to param)
                            if total_price < float(low_price):
                                found_deal = True
                            else:
                                continue

                        elif flight_details == "multi-leg":
                            # Only print if itinerary has >1 segment
                            multi_leg_itineraries = [
                                it for it in flight_offer["itineraries"] if len(it["segments"]) > 1
                            ]
                            if not multi_leg_itineraries:
                                continue
                            if total_price < float(low_price):
                                found_deal = True
                            else:
                                continue

                        else:  # both
                            if total_price < float(low_price):
                                found_deal = True
                            else:
                                continue

                        # Print flight offer details
                        print(f"\n🔥 Breaking Deal! {city} - {total_price} {currency}")
                        print(f"Price: {total_price} {currency}")
                        print("Itinerary:")
                        # If multi-leg only, print only multi-leg itineraries
                        itineraries_to_print = flight_offer["itineraries"]
                        if flight_details == "multi-leg":
                            itineraries_to_print = [
                                it for it in flight_offer["itineraries"] if len(it["segments"]) > 1
                            ]
                        for itinerary in itineraries_to_print:
                            for i, segment in enumerate(itinerary["segments"], 1):
                                dep = segment["departure"]
                                arr = segment["arrival"]
                                dep_time = dep["at"].replace("T", " ")
                                arr_time = arr["at"].replace("T", " ")
                                dep_iata = dep["iataCode"]
                                arr_iata = arr["iataCode"]
                                dep_term = dep.get("terminal", "N/A")
                                arr_term = arr.get("terminal", "N/A")

                                print(f"  Segment {i}:")
                                print(f"    Departure: {dep_time} from {dep_iata} terminal {dep_term}")
                                print(f"    Arrival:   {arr_time} at {arr_iata} terminal {arr_term}")
                        print("\n---\n")

                    if not found_deal:
                        print(f"No {flight_details} flights under {low_price} USD found on {formatted_date} for {city}.")

                except requests.exceptions.RequestException as e:
                    print(f"⚠️ Error fetching flight for {formatted_date} to {iata}: {e}")
