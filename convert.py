import pandas as pd
import json

# Load the JSON data from the file
with open('restaurant_data.json', 'r') as file:
    data = json.load(file)

# Normalize the main data
df_main = pd.json_normalize(data)

# Extract and normalize the 'Open Hours' data
open_hours_data = []
for restaurant in data:
    name = restaurant['RestaurantName']
    for day, hours in restaurant['Open Hours'].items():
        for time_slot in hours:
            open_hours_data.append({
                'RestaurantName': name,
                'Day': day,
                'Hours': time_slot
            })

# Create a DataFrame for the 'Open Hours' data
df_open_hours = pd.DataFrame(open_hours_data)

# Save the data to an Excel file
with pd.ExcelWriter('restaurants_data.xlsx') as writer:
    df_main.to_excel(writer, sheet_name='Main Data', index=False)
    df_open_hours.to_excel(writer, sheet_name='Open Hours', index=False)

print("Data has been successfully saved to restaurants_data.xlsx")
