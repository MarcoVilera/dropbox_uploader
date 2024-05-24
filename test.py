import datetime
import re

# Assuming file_name is in the format 'GLOBAL_C_CONT_20240501_100148.bak'
match = re.search(r'^(.*?)_(\d{4}\d{2})01_(\d{6})\.bak$', "I_GLOBAL_ADM_20240101_210000.bak")
if match:
    prefix = match.group(1)  # Extract the prefix
    date_str = match.group(2)  # Extract the year and month part
    file_date = datetime.datetime.strptime(date_str, '%Y%m')  # Convert to datetime object

    current_month = datetime.datetime.now().month  # Get current month
    file_month = file_date.month  # Get month from file date
    file_year = file_date.year  # Get year from file date

    if file_month < current_month or file_year < datetime.datetime.now().year:
        print(f"The file '{prefix}' is from a past month.")
    elif file_month == current_month:
        print(f"The file '{prefix}' is from the current month.")
    else:
        print(f"The file '{prefix}' is from a future month.")