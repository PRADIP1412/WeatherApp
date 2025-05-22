from django.shortcuts import render
from django.contrib import messages
import datetime
import requests
from django.conf import settings

# Create your views here.
def home(request):
    city = 'ahmedabad'
    if 'city' in request.POST:
        city = request.POST['city'].strip()

    OPEN_WEATHER_API_KEY = settings.OPEN_WEATHER_API_KEY

    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API_KEY}&units=metric'

    SEARCH_ENGINE_API_KEY = settings.SEARCH_API_KEY
    SEARCH_ENGINE_ID = settings.SEARCH_ENGINE_ID

    query = city + " city 1920x1080" 
    page = 1
    start = (page - 1) * 10 + 1
    searchType = 'image'
    imgSize = 'xlarge'
    city_image_search_url = f"https://www.googleapis.com/customsearch/v1?key={SEARCH_ENGINE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&searchType={searchType}&imgSize={imgSize}"

    image_url = 'https://images.pexels.com/photos/3008509/pexels-photo-3008509.jpeg?auto=compress&cs=tinysrgb&w=1600' # Default image
    try:
        image_data = requests.get(city_image_search_url).json()
        search_items = image_data.get("items")
        if search_items and len(search_items) > 1: 
            image_url = search_items[1]['link']
        elif search_items and len(search_items) > 0: 
            image_url = search_items[0]['link']
    except Exception as e:
        messages.warning(request, f"An unexpected error occurred while fetching image: {e}")
  
    weather_data = {}
    exception_occurred = False
    
    try:
        response = requests.get(weather_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Corrected API access
        weather_data['description'] = data['weather'][0]['description']
        weather_data['icon'] = data['weather'][0]['icon']
        weather_data['temp'] = data['main']['temp'] # Corrected: no [0] here
        weather_data['day'] = datetime.date.today()
        weather_data['city'] = data['name'] # Use city name from API response for accuracy
        weather_data['exception_occurred'] = False

    except Exception as e:
        # Catch any other unexpected errors
        messages.error(request, f'An unexpected error occurred: {e}')
        exception_occurred = True

    # If an exception occurred during weather data fetching, use default values
    if exception_occurred:
        weather_data['description'] = 'Clear sky'
        weather_data['icon'] = '01d'
        weather_data['temp'] = 25
        weather_data['day'] = datetime.date.today()
        # Keep the searched city, not hardcode to ahmedabad
        weather_data['city'] = city if city else 'ahmedabad' # Use searched city, fallback to ahmedabad
        weather_data['exception_occurred'] = True
        
    return render(request, 'weatherapp/index.html', {
        'description' : weather_data.get('description', 'N/A'), # Use .get() with default values
        'icon' : weather_data.get('icon', '01d'),
        'temp' : weather_data.get('temp', 25),
        'day' : weather_data.get('day', datetime.date.today()),
        'city' : weather_data.get('city', 'ahmedabad'),
        'exception_occurred' : weather_data.get('exception_occurred', False),
        'image_url': image_url, # Pass the dynamically found or default image URL
    })