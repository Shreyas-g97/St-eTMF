import streamlit as st
import pandas as pd
import os
import mysql.connector
from mysql.connector import Error
import csv
import config

def create_server_connection(host_name, user_name, user_password, database_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=database_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Query executed successfully")
        return cursor.fetchall()
    except Error as err:
        print(f"Error: '{err}'")


def main():
    st.title("eTMF Data Upload App")

    # Upload spreadsheet document
    file = st.file_uploader("Upload a spreadsheet", type=["csv", "xls", "xlsx"])

    if file is not None:
        file_extension = file.name.split(".")[-1]

        try:
            if file_extension == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            st.write("Spreadsheet Contents:")
            st.dataframe(df)

            # Establish a connection to the MySQL database
            connection = create_server_connection("localhost", "root", config.DATABASE_PASS, "testdb")  # Replace with your MySQL connection details

            # Insert the data into the MySQL database
            save_file(df, file.name, connection)

            # Specify the folder path
            folder_path = "data"

            # Create the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            cursor = connection.cursor()

            # Define your SQL query
            query_missing = "SELECT No, Comment FROM etmf WHERE Comment LIKE '%missing%' OR Comment LIKE '%MISSING%';"
            cursor.execute(query_missing)
            # Fetch all the rows returned by the query
            rows = cursor.fetchall()

            # Convert the rows to string sentences
            sentences = []
            for row in rows:
                no = row[0]
                comment = row[1]
                sentence = f"No: {no}, Comment: {comment}"
                sentences.append(sentence)

            # Close the database connection
            connection.close()

            # Save the sentences to a CSV file in the specified folder
            # csv_file_path = os.path.join(folder_path, "sentences.csv")
            # with open(csv_file_path, "w", newline="") as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(["No", "Comment"])  # Write the header row
            #     for sentence in sentences:
            #         # Extract 'no' and 'comment' from the sentence
            #         no, comment = sentence.split(", ")
            #         writer.writerow([no.split(":")[1].strip(), comment.split(":")[1].strip()])  # Write each sentence as a row


            # Display the sentences on Streamlit
            st.write("Missing Documents:")
            for sentence in sentences:
                st.write(sentence)
                

            # Display success message
            # st.success("Data saved to MySQL database")

        except Exception as e:
            st.error(f"Error: {e}")


def save_file(df, filename, connection):
    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Create a table in the database to store the CSV data
        table_name = "eTMF"  # Replace with your desired table name

        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (No nvarchar(50), Category nvarchar(50), `Document Name` nvarchar(50), Version nvarchar(50), Date nvarchar(100), Signature nvarchar(50), Comment nvarchar(150), `Additional Notes` nvarchar(500))"  # Replace DATATYPE with appropriate column types
        cursor.execute(create_table_query)

        # Insert the data into the table
        for _, row in df.iterrows():
            insert_query = f"INSERT INTO {table_name} (`No`, `Category`, `Document Name`, `Version`, `Date`, `Signature`, `Comment`, `Additional Notes`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"  # Replace column names and placeholders as per your CSV
            values = (row['No'], row['Category'], row['Document Name'], row['Version'], row['Date'], row['Signature'], row['Comment'], row['Additional Notes'])  # Replace column names as per your CSV
            cursor.execute(insert_query, values)

        # Commit the changes to the MySQL database
        connection.commit()
        st.success("Data inserted successfully!")
    except Error as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
