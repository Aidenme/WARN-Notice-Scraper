from bs4 import BeautifulSoup
import requests
import csv
import re

class Site:
    def __init__(self):
        self.full_table = None
        self.page_url = "http://reactwarn.floridajobs.org/WarnList/Records?year=2020&page="
        self.start_page = 1
        self.total_pages = 1

    def get_site_data(self):
        site_data_list = []
        start_page_url = self.page_url
        total_pages = self.total_pages
        starting_page = self.start_page

        while starting_page <= total_pages:
            pages_url = start_page_url + str(starting_page)
            soup = self.get_soup(pages_url)
            site_data_list = site_data_list + self.get_rows_from_page(soup)
            print(starting_page)
            starting_page += 1

        self.full_table = site_data_list

    def get_soup(self, url):
        html_content = requests.get(url)
        soup = BeautifulSoup(html_content.text, "html5lib")
        return soup

    def get_rows_from_page(self, soup):
        all_rows = []
        table_rows = soup.tbody.find_all('tr')
        table_header = soup.thead.find_all('th')
        all_rows.append(table_header)
        for row in table_rows:
            table_data = row.find_all(['td', 'th'])
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
        self.company_column_eq = 0
        self.effective_date_column = None
        self.location_column = None
        self.worker_count_column = None
        self.final_table = None

    def print_raw_table(self):
        for row in self.raw_table:
            print(row)

    def set_raw_table_column_names(self):
        print(self.raw_table[0])

    def clean_column_company(self):
        company_column_raw = self.get_column(self.company_column_eq)
        company_column_clean = []
        location_clean = []
        for row in company_column_raw:
            split_list = str(row).split('>')
            #The company name is always the third element in the list after a split along the > part of the html syntax
            company_name = split_list[2]
            company_name = company_name.replace('</b', '')
            company_name = company_name.replace('&amp;', '&')
            company_column_clean.append(company_name)
        for row in company_column_clean:
            print(row)

    def get_column(self, column_index):
        column = []
        for row in self.raw_table:
            column.append(row[column_index])
        return column





def clean_row(row_list):
    row_list = [clean_row_item(row) for row in row_list]
    row_list[5] = clean_download_link(row_list[5])
    return row_list

def clean_row_item(item):
    item = str(item)
    item = re.sub("<td>|</td>|<b>|</b>|<i>|</i>", "", item)
    item = re.sub("<br/>", "\n", item)
    return item

def clean_download_link(item):
    link_start = "http://reactwarn.floridajobs.org"
    item = re.sub('<a href=|"|>Download</a>', "", item)
    item = link_start + item
    return item

def clean_raw_list(list):
    cleaned_rows = []
    for row in list:
        cleaned_rows.append(clean_row(row))
    return cleaned_rows

def create_csv_file():
    raw_list_rows = get_site_data()
    final_list = clean_raw_list(raw_list_rows)
    column_names = ['Company Name', 'Layoff Date', 'Employees Affected']
    with open('FL_WARN_Notice.csv', mode='w+') as csv_file:
        warn_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        warn_writer.writerow(column_names)
        for row in final_list:
            warn_writer.writerow(row)

#create_csv_file()

fl_site = Site()
fl_site.get_site_data()
fl_table = MyTable(fl_site.full_table)
#fl_table.print_raw_table()
#fl_table.set_raw_table_column_names()
fl_table.clean_column_company()
