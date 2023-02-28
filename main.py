import os
import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Retrieve bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Create a bot from the TeleBot class
bot = telebot.TeleBot(BOT_TOKEN)


# Define a message handler that handles incoming /start and /hello commands
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_button = KeyboardButton(text="Share location 📍", request_location=True)
    keyboard.add(location_button)
    bot.send_message(message.chat.id,
                     "To get started, please share your location with me by clicking the button below.",
                     reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def handle_location(message):

    # Get lon and lat from the user's shared location
    longitude = message.location.longitude
    latitude = message.location.latitude

    # Get the nearest breweries from Open Brewery DB API
    breweries = get_nearest_breweries(latitude, longitude)

    # format response message with brewery information
    if breweries:
        message_text = "Here are the nearest breweries:\n\n"

        # Initialize list to hold brewery data
        brewery_data = []

        for brewery in breweries:
            name = brewery.get("name", "")
            address = brewery.get("street", "") + ", " + brewery.get("city", "") + ", " + brewery.get("state", "")
            website = brewery.get("website_url", "")
            lat = brewery.get("latitude", "")
            lon = brewery.get("longitude", "")
            if lat and lon:
                directions_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"
                brewery_data.append({"name": name,
                                     "address": address,
                                     "website": website,
                                     "directions_url": directions_url})
                message_text += f"{name}\n{address}\nWebsite: {website}\n\n"
            else:
                message_text += f"{name}\n{address}\nWebsite: {website}\n\n"

        # create inline keyboard with buttons for each brewery directions
        keyboard = InlineKeyboardMarkup()
        for data in brewery_data:
            keyboard.add(InlineKeyboardButton(f"Directions: {data['name']}", url=data['directions_url']))

        # send message with inline keyboard
        bot.send_message(message.chat.id, message_text, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Sorry, I could not find any breweries near your location.")


# Get three nearest breweries from Open Brewery DB
def get_nearest_breweries(latitude, longitude):
    endpoint = "https://api.openbrewerydb.org/breweries"
    params = {
        "by_dist": f"{latitude},{longitude}",
        "per_page": 3
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Launch the bot
bot.infinity_polling()
