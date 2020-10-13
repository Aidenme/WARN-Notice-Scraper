from bs4 import BeautifulSoup
import requests
import csv
import re

class Site:
    def __init__(self):
        self.full_table = None
        self.page_url = "http://reactwarn.floridajobs.org/WarnList/Records?year=2020&page="
        self.start_page = 1
        self.total_pages = 13

    def get_site_data(self):
        site_data_list = []
        start_page_url = self.page_url
        total_pages = self.total_pages
        starting_page = self.start_page

        while starting_page <= total_pages:
            pages_url = start_page_url + str(starting_page)
            soup = self.get_soup(pages_url)
            site_data_list = site_data_list + self.get_rows_from_page(soup)
            print("Got data from website page " + str(starting_page))
            starting_page += 1

        self.full_table = site_data_list

    def get_soup(self, url):
        html_content = requests.get(url)
        soup = BeautifulSoup(html_content.text, "html5lib")
        return soup

    def get_rows_from_page(self, soup):
        all_rows = []
        table_rows = soup.tbody.find_all('tr')
        for row in table_rows:
            table_data = row.find_all('td')
            all_rows.append(table_data)
        return all_rows

    def print_site_data(self):
        for row in self.table:
            print(row)

class MyTable:
    def __init__(self, site_table):
        self.raw_table = site_table
        self.raw_table_column_names = None
        self.company_column = None
        self.company_column_index = 0
        self.effective_date_column = None
        self.effective_date_column_index = 2
        self.location_column = None
        self.location_column_index = 0
        self.worker_count_column = None
        self.worker_count_column_index = 3
        self.final_table = []

    def clean_data(self):
        self.clean_column_company()
        self.clean_column_effective_date()
        self.clean_column_location()
        self.clean_column_worker_count()

    def print_raw_table(self):
        for row in self.raw_table:
            print(row)

    def clean_column_company(self):
        company_column_raw = self.get_column(self.company_column_index)
        #remove first element from company column. This is the column name and not a company name so must be removed.
        company_column_clean = []
        location_clean = []
        for row in company_column_raw:
            split_list = str(row).split('>')
            #The company name is always the third element in the list after a split along the > part of the html syntax.
            company_name = split_list[2]
            company_name = company_name.replace('</b', '')
            company_name = company_name.replace('&amp;', '&')
            company_column_clean.append(company_name)
            #Getting the location. Might as well since it appears in the same data cell as the company name.
            address = []
            address_line_one = split_list[4]
            address_line_two = split_list[5]
            address_line_three = split_list[6]
            address_line_one = address_line_one.replace('<br/', '')
            address_line_two = address_line_two.replace('<br/', '')
            address_line_three = address_line_three.replace('</td', '')
            address.append(address_line_one)
            #2nd address line is optional. It won't be part of the address if it doesn't exist.
            if address_line_two != '':
                address.append(address_line_two)
            address.append(address_line_three)
            #Join individual address lines into one address string.
            location_clean.append('\n'.join(address))
        self.company_column = company_column_clean
        self.location_column = location_clean

    def clean_column_effective_date(self):
        effective_date_column_raw = self.get_column(self.effective_date_column_index)
        effective_date_column_clean = []
        for row in effective_date_column_raw:
            date_range = re.sub("<td>|</td>|<br/>|<i>|</i>", "", str(row))
            effective_date_column_clean.append(date_range)
        self.effective_date_column = effective_date_column_clean

    def clean_column_location(self):
        #This is handled in clean_column_company()
        pass

    def clean_column_worker_count(self):
        worker_count_column_raw = self.get_column(self.worker_count_column_index)
        worker_count_column_clean = []
        for row in worker_count_column_raw:
            worker_count = re.sub("<td>|</td>", "", str(row))
            worker_count_column_clean.append(worker_count)
        self.worker_count_column = worker_count_column_clean


    def get_column(self, column_index):
        column = []
        for row in self.raw_table:
            column.append(row[column_index])
        return column

    def create_final_table(self):
        i = 0
        while i < len(self.company_column):
            table_row = []
            table_row.append(self.company_column[i])
            table_row.append(self.effective_date_column[i])
            table_row.append(self.location_column[i])
            table_row.append(self.worker_count_column[i])
            self.final_table.append(table_row)
            i += 1

class CSVMaster:
    def __init__(self, table):
        self.table = table
        self.column_names = ["Company", "Effective Date", "Location", "Number of Workers"]

    def create_csv_file(self):
        with open('FL_WARN_Notice.csv', mode='w+') as csv_file:
            warn_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            warn_writer.writerow(self.column_names)
            for row in self.table.final_table:
                warn_writer.writerow(row)

fl_site = Site()
fl_site.get_site_data()
fl_table = MyTable(fl_site.full_table)
fl_table.clean_column_company()
fl_table.clean_data()
fl_table.create_final_table()
fl_csv = CSVMaster(fl_table)
fl_csv.create_csv_file()
