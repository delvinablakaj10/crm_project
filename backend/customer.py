import os
from datetime import datetime, timedelta

import pandas as pd


class CRMBackend:
    def __init__(self, file_path='customers.csv'):
        self.file_path = file_path
        self.df = self.load_or_create_csv()

    def load_or_create_csv(self):
        #Loads or creates a CSV file to store customer data
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=['ID', 'Name', 'Email', 'Phone Number', 'Address', 'Company', 'Date Added'])
            df.to_csv(self.file_path, index=False)
        else:
            df = pd.read_csv(self.file_path)
        return df

    def add_customer(self, customer):
        #Adds a new customer to the DataFrame and saves it.
        self.df = pd.concat([self.df, pd.DataFrame([customer])], ignore_index=True)
        self.df.to_csv(self.file_path, index=False)

    def update_customer(self, index, updated_data):
        # Update the customer data at the given index
        for key, value in updated_data.items():
            self.df.at[index, key] = value

    def delete_customer(self, index):
        #Deletes a customer from the DataFrame
        self.df.drop(index, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.df.to_csv(self.file_path, index=False)

    def update_dashboard(self):
        #Returns infos for the dashboard
        total_customers = len(self.df)
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_additions = len(self.df[pd.to_datetime(self.df['Date Added']) >= recent_cutoff])
        return total_customers, recent_additions
