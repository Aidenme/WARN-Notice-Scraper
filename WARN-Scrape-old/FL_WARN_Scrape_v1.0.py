from bs4 import BeautifulSoup
import requests
import csv
import re

def get_rows_from_page(soup):
    all_rows = []
    table_rows = soup.tbody.find_all('tr')
    for row in table_rows:
        table_data = row.find_all('td')
        all_rows.append(table_data)
    return all_rows

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

def get_site_data():
    page_nix_page_number = "http://reactwarn.floridajobs.org/WarnList/Records?year=2020&page="
    site_data_list = []
    total_pages = 11
    starting_page = 1

    while starting_page <= total_pages:
        pages_url = page_nix_page_number + str(starting_page)
        soup = get_soup(pages_url)
        site_data_list = site_data_list + get_rows_from_page(soup)
        print(starting_page)
        starting_page += 1

    return site_data_list

def get_soup(url):
    html_content = requests.get(url)
    soup = BeautifulSoup(html_content.text, "html5lib")
    return soup

def clean_raw_list(list):
    cleaned_rows = []
    for row in list:
        cleaned_rows.append(clean_row(row))
    return cleaned_rows

def create_csv_file():
    raw_list_rows = get_site_data()
    final_list = clean_raw_list(raw_list_rows)
    column_names = ['Company Name', 'State Notification Date', 'Layoff Date', 'Employees Affected', 'Industry', 'PDF Link']
    with open('FL_WARN_Notice.csv', mode='w+') as csv_file:
        warn_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        warn_writer.writerow(column_names)
        for row in final_list:
            warn_writer.writerow(row)

create_csv_file()
