import app.models.astronomer as Astronomer
import app.database.connector as connector
import app.data.get.countries as countries_data
import app.data.get.astronomers as astronomers_data

# Variables
conn = connector.get_db_connection()

# Functions
# Transform astronomers
def transform_astronomers(astronomers):
    transformed_astronomers = []
    for astronomer in astronomers:
        transformed_astronomer = Astronomer.Astronomer(
            astronomer[0], # id
            astronomer[1], # name
            astronomer[2], # birth_year
            astronomer[3], # death_year
            astronomer[4].split(", ") if astronomer[4] else [] # nationalities
        )
        transformed_astronomers.append(transformed_astronomer.to_dict())
    return transformed_astronomers

# Upload astronomer_country
def upload_astronomers_countries(astronomer_name:str, countries_list:list):
    for country_name in countries_list:
        try:
            cur = conn.cursor()
            cur.execute("CALL insert_astronomer_country(%s, %s);", (astronomer_name, country_name))
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error uploading astronomer_country: {e}")
            conn.rollback()
            raise e

def upload_astronomers():
    # Get astronomers and countries
    astronomers = astronomers_data.get_astronomers()
    countries_names = countries_data.get_countries_names()

    try:
        for astronomer in astronomers:
            if set(astronomer["countries"]).issubset(countries_names):
                cur = conn.cursor()
                cur.execute("CALL insert_astronomer(%s, %s, %s);", 
                            (astronomer["name"], astronomer["birth_year"], astronomer["death_year"]))
                conn.commit()
                cur.close()
                upload_astronomers_countries(astronomer["name"], astronomer["countries"])
    except Exception as e:
        print(f"Error uploading astronomers: {e}")
        conn.rollback()
        raise e

# Get astronomers
def get_astronomers(offset, limit):
    """
    Get paginated astronomers from the database using a user-defined function
    """
    try:
        cur = conn.cursor()

        # Call the user-defined function to get paginated astronomers
        cur.execute("SELECT id, name, birth_year, death_year, countries \
                    FROM get_paginated_astronomers(%s, %s)", (offset, limit))
        astronomers = cur.fetchall()
        cur.close()
        t_astronomers = transform_astronomers(astronomers)
        return t_astronomers
    except Exception as e:
        print(f"Error getting astronomers: {e}")
        raise e

# Get astronomers count
def get_astronomers_count():
    try:
        cur = conn.cursor()
        cur.execute("CALL get_astronomers_count(%s);", (None,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error performing query to check astronomers: {e}")
        return 0

# Get astronomers by country
def get_astronomers_by_country(country_name:str, offset:int, limit:int):
    try:
        cur = conn.cursor()

        # Call the user-defined function to get paginated astronomers
        cur.execute("SELECT id, name, birth_year, death_year, countries \
                    FROM get_astronomers_by_country(%s, %s, %s)", (country_name, offset, limit))
        astronomers = cur.fetchall()
        cur.close()
        t_astronomers = transform_astronomers(astronomers)
        return t_astronomers
    except Exception as e:
        print(f"Error getting astronomers: {e}")
        raise e