
import os
import sys

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from email_service import send_weather_email

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.
    
    Args:
        city: Name of the city, such as Bengaluru or London.
    """
    if not OPENWEATHER_API_KEY:
        return "Error: OPENWEATHER_API_KEY is not configured."

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]

        return (
            f"Weather in {data['name']}, {data['sys']['country']}:\n"
            f"Condition: {description.title()}\n"
            f"Temperature: {temperature} °C\n"
            f"Feels like: {feels_like} °C\n"
            f"Humidity: {humidity}%\n"
            f"Wind speed: {wind_speed} m/s"
        )

    except requests.HTTPError as exc:
        if exc.response.status_code == 404:
            return f"Error: City '{city}' was not found."
        return f"Weather API error: {exc}"

    except requests.RequestException as exc:
        return f"Network error: {exc}"

    except (KeyError, IndexError, ValueError):
        return "Error: Unexpected weather API response."


agent = create_agent(
    model="openai:gpt-4.1-mini",
    tools=[get_weather],
    system_prompt=(
        "You are a weather assistant. Use the get_weather tool "
        "to retrieve current weather for the requested city. "
        "Report the returned weather details clearly. "
        "Never invent weather data."
    ),
)


def main(city: str) -> None:
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Get the current weather for {city}.",
                }
            ]
        }
    )

#     # Print the final response from the agent.
#     final_message = result["messages"][-1]
#     print(final_message.content)


# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print('Usage: python weather_agent.py "Bengaluru"')
#         sys.exit(1)

#     city = " ".join(sys.argv[1:]).strip()

#     if not city:
#         print("Error: Please provide a city name.")
#         sys.exit(1)

#     main(city)


    # Step 2: Extract weather output
    weather_output = result["messages"][-1].content

    if not isinstance(weather_output, str):
        weather_output = str(weather_output)

    # Step 3: Print output
    print("\n===== WEATHER REPORT =====")
    print(weather_output)

    # Step 4: Send email after printing
    try:
        send_weather_email(city, weather_output)

    except Exception as error:
        print(f"Failed to send email: {error}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python weather_agent.py "Bengaluru"')
        sys.exit(1)

    city = " ".join(sys.argv[1:]).strip()

    if not city:
        print("Please provide a city name.")
        sys.exit(1)

    main(city)
