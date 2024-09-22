from datetime import datetime, timedelta

import pandas as pd
from backend.customer import CRMBackend
from backend.validation import is_valid_email, is_valid_phone_number
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

# Declare constants for widgets
LAYOUT_PADDING = [20, 10, 20, 10]
FIELD_SIZE = (700, 80)
LABEL_SIZE = (100, 40)
BUTTON_HEIGHT = 80
GRID_SPACING = 10

class CRMApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend = CRMBackend()
        self.current_editing_row = None
        self.inputs = {}

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=LAYOUT_PADDING, spacing=GRID_SPACING)
        self.create_dashboard()
        self.create_form()
        self.create_search_filter()
        self.create_customer_table()
        self.view_customers()
        return self.layout

    def create_form(self):
        #Creates form layout for adding/editing customers with equal spacing for columns
        self.form_layout = GridLayout(cols=2, size_hint=(1, None), height=460, spacing=GRID_SPACING)
        
        fields = [('Name', 'Name'), ('Email', 'Email'), ('Phone Number', 'Phone Number'), 
                ('Address', 'Address'), ('Company', 'Company')]
        
        for label_text, hint_text in fields:
            self.add_form_field(label_text, hint_text)
        
        self.layout.add_widget(self.form_layout)

        # Create a BoxLayout to center the Add Customer button
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=BUTTON_HEIGHT)
        
        self.add_button = Button(text='Add Customer', size_hint=(None, None), width=450,padding=[10,10,10,10], height=BUTTON_HEIGHT)
        self.add_button.bind(on_press=self.add_customer)

        # Add button to button_layout and center it
        button_layout.add_widget(Widget(size_hint_x=None, width=0)) 
        button_layout.add_widget(self.add_button)
        button_layout.add_widget(Widget(size_hint_x=None, width=0)) 

        self.layout.add_widget(button_layout)



    def add_form_field(self, label_text, hint_text):
        #Helper to add a labeled input field to the form
        label = Label(text=f'{label_text}:', size_hint_x=0.2, size_hint_y=None, height=LABEL_SIZE[1])
        input_field = TextInput(hint_text=hint_text, size_hint_x=0.5, size_hint_y=None, height=FIELD_SIZE[1])  
        self.inputs[label_text] = input_field
        self.form_layout.add_widget(label)
        self.form_layout.add_widget(input_field)

    def create_dashboard(self):
        #Creates a dashboard that shows key customer metrics
        self.dashboard_layout = GridLayout(cols=2, size_hint=(1, None), height=100, spacing=GRID_SPACING)
        self.total_customers_label = Label(text="Total Customers: 0", size_hint=(None, None), size=(200, 40), font_size=20)
        self.recent_additions_label = Label(text="Recent Additions (7 days): 0", size_hint=(None, None), size=(300, 40), font_size=20)
        
        self.dashboard_layout.add_widget(self.total_customers_label)
        self.dashboard_layout.add_widget(self.recent_additions_label)
        self.layout.add_widget(self.dashboard_layout)


    def update_dashboard(self):
        """Updates the dashboard with the latest metrics."""
        total_customers = len(self.backend.df)
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_additions = len(self.backend.df[pd.to_datetime(self.backend.df['Date Added']) >= recent_cutoff])

        self.total_customers_label.text = f"Total Customers: {total_customers}"
        self.recent_additions_label.text = f"Recent Additions (7 days): {recent_additions}"

    def create_search_filter(self):
        #Creates a search bar and filter dropdown
        self.search_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=GRID_SPACING)
        self.search_input = TextInput(hint_text="Search...", size_hint=(0.7, 1), multiline=False)
        self.search_input.bind(text=self.filter_customers)

        # Dropdown filter
        self.dropdown = DropDown()
        self.filter_criteria_button = Button(text='Filter by Name', size_hint=(0.3, 1))
        self.filter_criteria_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.filter_criteria_button, 'text', x))

        # Adding filter options
        self.add_filter_options(['Name', 'Email', 'Company'])

        self.search_layout.add_widget(self.search_input)
        self.search_layout.add_widget(self.filter_criteria_button)
        self.layout.add_widget(self.search_layout)



    def add_filter_options(self, options):
        #Helper to add filter options to the dropdown.
        for option in options:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)

    def add_row(self, row, index):
        # Adds a row in the customer table
        columns = ['ID', 'Name', 'Email', 'Phone Number', 'Address', 'Company']
        for col in columns:
            self.table_layout.add_widget(Label(text=str(row[col]) if pd.notna(row[col]) else ''))

        #Add Edit/Delete buttons
        row_buttons_layout = BoxLayout(orientation='horizontal', size_hint=(1, None))
        edit_button = Button(text='Edit', size_hint=(0.5, 1), on_press=lambda instance: self.edit_customer(index))
        delete_button = Button(text='Delete', size_hint=(0.5, 1), on_press=lambda instance: self.delete_customer(index))
        row_buttons_layout.add_widget(edit_button)
        row_buttons_layout.add_widget(delete_button)
        self.table_layout.add_widget(row_buttons_layout)

    def add_customer(self, instance):
        #Adds a new customer
        customer_data = {key: self.inputs[key].text for key in self.inputs}
        if not customer_data['Name'] or not customer_data['Email']:
            print("Error: Name and Email must be provided.")
            return

        if not is_valid_email(customer_data['Email']) or not is_valid_phone_number(customer_data['Phone Number']):
            print("Error: Invalid input format.")
            return

        new_customer = {**customer_data, 'ID': len(self.backend.df) + 1, 'Date Added': datetime.now().strftime('%Y-%m-%d')}
        self.backend.add_customer(new_customer)
        self.refresh_customers()

    def save_customer(self):
        #Saves changes to the customer currently being edited.
        if self.current_editing_row is not None:
            customer_data = {key: self.inputs[key].text for key in self.inputs}
            self.backend.update_customer(self.current_editing_row, customer_data)
            self.current_editing_row = None
            self.add_button.text = 'Add Customer'
            self.refresh_customers()

    def edit_customer(self, index):
        #Populates the form fields for editing an existing customer.
        customer = self.backend.df.iloc[index]
        
        # Ensure all fields are handled correctly as strings
        for key in self.inputs:
            field_value = customer[key]
            # Only apply replace if the value is a string
            if isinstance(field_value, str):
                field_value = field_value.replace(u'\r\n', u'\n')
            
            self.inputs[key].text = str(field_value) 

        self.current_editing_row = index
        self.add_button.text = 'Save Changes'


    def delete_customer(self, index):
        #Deletes a customer from the system.
        self.backend.delete_customer(index)
        self.refresh_customers()

    def create_customer_table(self):
        #Creates a scrollable table layout for displaying customer data.
        self.scroll_view = ScrollView(size_hint=(1, None), size=(600, 400))
        top_spacer = Widget(size_hint_y=None, height=20)  # Adjust height as needed
        self.table_layout = GridLayout(cols=7, size_hint_y=None)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))
        self.scroll_view.add_widget(self.table_layout)
        self.layout.add_widget(top_spacer)  # Add the spacer to the layout
        self.layout.add_widget(self.scroll_view)
    
    def view_customers(self):
        #Displays the customers in the table.
        self.table_layout.clear_widgets()
        headers = ['ID', 'Name', 'Email', 'Phone', 'Address', 'Company', 'Actions']
        for header in headers:

            self.table_layout.add_widget(Label(text=header, bold=True))
        for index, row in self.backend.df.iterrows():
            self.add_row(row, index)

    def filter_customers(self, instance, query):
        #Filters customers based on the search input and filter criteria.
        filter_criteria = self.filter_criteria_button.text
        if filter_criteria in self.backend.df.columns:
            filtered_df = self.backend.df[self.backend.df[filter_criteria].str.contains(query, case=False, na=False)]
            self.table_layout.clear_widgets()
            for index, row in filtered_df.iterrows():
                self.add_row(row, index)

    def refresh_customers(self):
        #Refreshes the customer table and dashboard.
        self.view_customers()
        self.update_dashboard()
        self.clear_inputs()

    def clear_inputs(self):
        #Clears the input fields
        for key in self.inputs:
            self.inputs[key].text = ''
        self.current_editing_row = None
        self.add_button.text = 'Add Customer'
