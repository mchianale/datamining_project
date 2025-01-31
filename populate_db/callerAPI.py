import requests


BASE_URL = "http://localhost:8000"

def check(url):
    sql_query = f"SELECT COUNT(*) AS count FROM films WHERE url='{url}'"
    data = {"sql_query" : sql_query}
    response = requests.post(f"{BASE_URL}/query", json=data)
    if response.status_code == 200:
        print(response.content)

def insert(table_name, data):
    name_values = ', '.join(data.keys())
    insert_values = ""
    for value in data.values():
        if value is None:
            insert_values +="null"
        elif type(value) == str:
            escaped_value = value.replace("'", "''")
            insert_values += f"'{escaped_value}'"
        else:
            insert_values += str(value)
        insert_values += ", "
    insert_values = insert_values[:-2]
    sql_query = f"""INSERT INTO {table_name} ({name_values}) VALUES ({insert_values});"""

    data = {"sql_query" : sql_query}
    response = requests.post(f"{BASE_URL}/execution", json=data)

    # Check if the request was successful
    return response.status_code == 200
