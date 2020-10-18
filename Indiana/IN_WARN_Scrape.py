from bs4 import BeautifulSoup
import requests
import csv
import re

class Site:
    def __init__(self):
        self.full_table = None
        #If there are multiple pages be sure to have the link with 'page='' in it and remove the page number.
        self.page_url = "https://www.in.gov/dwd/2567.htm"
        self.start_page = 1
        self.total_pages = 1
        self.multi_page = False

    def get_site_data(self):
        site_data_list = []
        start_page_url = self.page_url
        total_pages = self.total_pages
        starting_page = self.start_page

        if self.multi_page == True:
            while starting_page <= total_pages:
                pages_url = start_page_url + str(starting_page)
                soup = self.get_soup(pages_url)
                site_data_list = site_data_list + self.get_rows_from_page(soup)
                print("Got data from website page " + str(starting_page))
                starting_page += 1
        else:
            soup = self.get_soup(self.page_url)
            site_data_list = self.get_rows_from_page(soup)

        self.full_table = site_data_list

    def get_soup(self, url):
        html_content = requests.get(url)
        soup = BeautifulSoup(html_content.text, "html5lib")
        return soup

    def get_rows_from_page(self, soup):
        all_rows = []
        table_rows = soup.find_all('tr')
        for row in table_rows:
            table_data = row.find_all('td')
            all_rows.append(table_data)
        return all_rows

    def print_site_data(self):
        for row in self.full_table:
            print(row)

class MyTable:
    def __init__(self, site_table):
        self.raw_table = site_table
        self.raw_table_column_names = None
        self.company_column = None
        self.company_column_index = 0
        self.effective_date_column = None
        self.effective_date_column_index = 4
        self.location_column = None
        self.location_column_index = 1
        self.worker_count_column = None
        self.worker_count_column_index = 2
        self.final_table = []

    def clean_data(self):
        self.clean_column_company()
        self.clean_column_effective_date()
        self.clean_column_location()
        self.clean_column_worker_count()

    def print_raw_table(self):
        for row in self.raw_table:
            print(row)

    def print_column(self, column):
        column_to_print = eval("self." + column)
        for row in column_to_print:
            print(row)

    def get_data_between_tags(self, row_string):
        list = re.split("<[^<>]+>", row_string)
        clean_list = []
        for row in list:
            row = re.sub(r"\n|\t|\xa0", "", row)
            row = row.replace("&amp;", "and")
            if row != '':
                clean_list.append(row)
        return clean_list

    def clean_column_company(self):
        company_column_raw = self.get_column(self.company_column_index)
        company_column_clean = []

        for row in company_column_raw:
            clean_row_list = self.get_data_between_tags(str(row))
            clean_row = clean_row_list[0]
            company_column_clean.append(clean_row)

        self.company_column = company_column_clean

    def clean_column_effective_date(self):
        effective_date_column_raw = self.get_column(self.effective_date_column_index)
        effective_date_column_clean = []
        name = "value to fill"
        for row in effective_date_column_raw:
            name = str(row).replace("<td>", "")
            name = name.replace("</td>", "")
            effective_date_column_clean.append(name)
        self.effective_date_column = effective_date_column_clean

    def clean_column_location(self):
        location_column_raw = self.get_column(self.location_column_index)
        location_column_clean = []

        for row in location_column_raw:
            clean_row_list = self.get_data_between_tags(str(row))
            clean_row = clean_row_list[0]
            location_column_clean.append(clean_row)

        self.location_column = location_column_clean

    def clean_column_worker_count(self):
        worker_count_column_raw = self.get_column(self.worker_count_column_index)
        worker_count_column_clean = []

        for row in worker_count_column_raw:
            clean_row_list = self.get_data_between_tags(str(row))
            if len(clean_row_list) > 1:
                clean_row = clean_row_list[0] + " " + clean_row_list[1]
            else:
                clean_row = row[0]
            print(clean_row)
            worker_count_column_clean.append(clean_row)

        self.worker_count_column = worker_count_column_clean


    def get_column(self, column_index):
        column = []
        for row in self.raw_table:
            try:
                column.append(row[column_index])
            except:
                pass
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
        self.final_table

class CSVMaster:
    def __init__(self, table):
        self.table = table
        self.state = "IN"
        self.column_names = ["Company", "Effective Date", "Location", "Number of Workers"]

    def create_csv_file(self):
        with open(self.state + '_WARN_Notice.csv', mode='w+') as csv_file:
            warn_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            warn_writer.writerow(self.column_names)
            for row in self.table.final_table:
                warn_writer.writerow(row)

in_site = Site()
in_site.get_site_data()
#in_site.print_site_data()
in_table = MyTable(in_site.full_table)
in_table.clean_column_worker_count()
#in_table.print_column("worker_count_column")
#in_table.get_data_between_tags('<td><a href="/dwd/files/AAA_Sales_Engineering_Inc.pdf" target="_self">')
#in_table.clean_data()
#in_table.create_final_table()
#in_csv = CSVMaster(in_table)
#in_csv.create_csv_file()
