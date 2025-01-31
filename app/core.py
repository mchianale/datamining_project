from fastapi import HTTPException
import mysql.connector as mysql
from dotenv import load_dotenv
import logging
import time
import os
import json

load_dotenv()

class MySQLManager:
    def __init__(self):
        """
        Connects to the MySQL database defined in the Docker Compose configuration.
        """
        self.user = os.getenv('USER')
        self.password = os.getenv('PASSWORD')
        self.database = os.getenv('DATABASE')
        self.host = os.getenv('HOST')  # Default: '127.0.0.1'
        self.port = 3306

        # Attempt to connect to the database with retries
        retry, max_retry = 1, 30
        while True:
            if retry > max_retry:
                logging.error(f"[DATABASE CONNECTION ERROR]: Failed to connect after {max_retry} attempts.")
                raise Exception("Database connection failed.")
            try:
                self.cnx = mysql.connect(
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    host=self.host,
                    port=self.port
                )
                break
            except Exception as e:
                logging.warning(f"Failed to connect to MySQL, attempt {retry}/{max_retry}...")
                retry += 1
                time.sleep(1)
        
        # Load database schema/commands from file and execute them
        try:
            commands = json.load(open("app/create_command.json", "r"))
            cursor = self.cnx.cursor()
            for table_name, command in commands.items():
                cursor.execute(command)
                logging.info(f"-- Table '{table_name}' was successfully created or loaded.")
            self.cnx.commit()
        except Exception as e:
            logging.error(f"Failed to execute schema creation commands: {str(e)}")
            raise
    
    # free query 
    def freeQuery(self, sql_query : str):
        try:
            cursor = self.cnx.cursor()
            cursor.execute(sql_query)

            rows = cursor.fetchall()
            # Get the column names from cursor.description
            columns = [desc[0] for desc in cursor.description]

            # Create a list of dictionaries where each dictionary maps column names to the corresponding row value
            results = []
            for row in rows:
                result_dict = {columns[i]: row[i] for i in range(len(columns))}
                results.append(result_dict)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while querying :\n{sql_query}\n: {str(e)}")
        
    def freeExecution(self, sql_query : str):
        try:
            cursor = self.cnx.cursor()
            cursor.execute(sql_query)
            self.cnx.commit()
            return f"Successfully executed :\n{sql_query}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while executing :\n{sql_query}\n: {str(e)}")