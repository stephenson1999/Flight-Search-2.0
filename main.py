from flight_analyze import FlightSearch
from datetime import datetime, timedelta
import time
import pprint
import requests
import random
# List of cities
sheet_data = [
    {"id": 1, "city": "Paris", "iataCode": "", "lowestPrice": 300},
    {"id": 2, "city": "Madrid", "iataCode": "", "lowestPrice": 200},
    {"id": 3, "city": "Rome", "iataCode": "", "lowestPrice": 300},
    {"id": 4, "city": "Milan", "iataCode": "", "lowestPrice": 300},
    {"id": 5, "city": "New York", "iataCode": "", "lowestPrice": 150},
    {"id": 6, "city": "Barcelona", "iataCode": "", "lowestPrice": 300},
    {"id": 7, "city": "London", "iataCode": "", "lowestPrice": 300},
    {"id": 8, "city": "Berlin", "iataCode": "", "lowestPrice": 300},
    {"id": 9, "city": "Bangkok", "iataCode": "", "lowestPrice": 300},
    {"id": 10, "city": "Istanbul", "iataCode": "", "lowestPrice": 300},
    {"id": 11, "city": "Melbourne", "iataCode": "", "lowestPrice": 300},
    {"id": 12, "city": "Munich", "iataCode": "", "lowestPrice": 300},
    {"id": 13, "city": "Las Vegas", "iataCode": "", "lowestPrice": 100},
    {"id": 14, "city": "Florence", "iataCode": "", "lowestPrice": 300},
    {"id": 15, "city": "Dublin", "iataCode": "", "lowestPrice": 300},
    {"id": 16, "city": "Venice", "iataCode": "", "lowestPrice": 300},
    {"id": 17, "city": "Athens", "iataCode": "", "lowestPrice": 300},
    {"id": 18, "city": "Orlando", "iataCode": "", "lowestPrice": 300},
    {"id": 19, "city": "Miami", "iataCode": "", "lowestPrice": 300},
    {"id": 20, "city": "San Francisco", "iataCode": "", "lowestPrice": 300},
    {"id": 21, "city": "Shanghai", "iataCode": "", "lowestPrice": 300},
    {"id": 22, "city": "Frankfurt", "iataCode": "", "lowestPrice": 300},
    {"id": 23, "city": "Washington", "iataCode": "", "lowestPrice": 300},
    {"id": 24, "city": "Mexico City", "iataCode": "", "lowestPrice": 300},
    {"id": 25, "city": "Phuket", "iataCode": "", "lowestPrice": 300},
    {"id": 26, "city": "Guangzhou", "iataCode": "", "lowestPrice": 300},
    {"id": 27, "city": "Nice", "iataCode": "", "lowestPrice": 300},
    {"id": 28, "city": "Palma de Mallorca", "iataCode": "", "lowestPrice": 300},
    {"id": 29, "city": "Honolulu", "iataCode": "", "lowestPrice": 300},
    {"id": 30, "city": "Beijing", "iataCode": "", "lowestPrice": 300},
    {"id": 31, "city": "Valencia", "iataCode": "", "lowestPrice": 300},
    {"id": 32, "city": "Shenzhen", "iataCode": "", "lowestPrice": 300},
    {"id": 33, "city": "Antalya", "iataCode": "", "lowestPrice": 300},
    {"id": 34, "city": "Edinburgh", "iataCode": "", "lowestPrice": 300},
    {"id": 35, "city": "Bologna", "iataCode": "", "lowestPrice": 300},
    {"id": 36, "city": "Verona", "iataCode": "", "lowestPrice": 300},
    {"id": 37, "city": "Delhi", "iataCode": "", "lowestPrice": 300},
    {"id": 38, "city": "Lima", "iataCode": "", "lowestPrice": 300},
    {"id": 39, "city": "Santiago", "iataCode": "", "lowestPrice": 300},
    {"id": 40, "city": "Cairo", "iataCode": "", "lowestPrice": 300}
]


ONIGIN_IATA = input("Step One: Please enter the Iata Code of you airport that you wish to departure (Fomate = Xxx):")
start_date =datetime.today() + timedelta(days=1)
end_date = datetime.today() + timedelta(days=180)
departure_start = start_date.strftime("%Y-%m-%d")
departure_end = end_date.strftime("%Y-%m-%d")

# Initialize FlightSearch
flight_search = FlightSearch()

updated_sheet_data = []
for item in sheet_data:
    time.sleep(random.randint(2,3))
    city = item["city"]
    try:
        item["iataCode"] = flight_search.get_iata_code(city)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(f"Rate limit hit. Sleeping for 10 seconds before retrying {city}...")
            time.sleep(10)
            item["iataCode"] = flight_search.get_iata_code(city)
        else:
            raise e
    updated_sheet_data.append(item)

city_data = {item['id']: item for item in updated_sheet_data}
flight_search.get_flights(city_data)






#1 min 20 sec to 1 min 40 sec


    


    




