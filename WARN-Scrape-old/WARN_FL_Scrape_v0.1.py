from bs4 import BeautifulSoup
import requests
import csv
import re

start_url = "http://reactwarn.floridajobs.org/WarnList/Records?year=2020&page=1"
html_content = requests.get(start_url)
soup = BeautifulSoup(html_content.text, "html5lib")
raw_list_rows = []
clean_list_rows = []
next_page_links = []
cleaned_rows = []
column_names = ['Company Name', 'State Notification Date', 'Layoff Date', 'Employees Affected', 'Industry', 'PDF Link']

def print_html():
    print(soup.prettify(formatter="html5"))

def fill_list_rows(soup):
    temp_list = []
    table_rows = soup.tbody.find_all('tr')
    for row in table_rows:
        table_data = row.find_all('td')
        temp_list.append(table_data)
    return temp_list

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

def get_data_from_row(row):
    #table_rows = soup.tbody.find_all('tr')
    table_data = table_rows[row].find_all('td')
    print(table_data)

def get_next_page_links(links_page):
    print("get_next_page_links() started with: " + links_page)
    page_links = []
    html = requests.get(links_page)
    page_soup = BeautifulSoup(html.text, "lxml")
    for link in page_soup.tfoot.find_all('a'):
        clean_link = link.get('href')
        if clean_link not in page_links:
            page_links.append(clean_link)
    return page_links

def get_all_page_links(first_url):
    url = first_url
    all_page_links = [url]
    root_url = "http://reactwarn.floridajobs.org"
    while True == True:
        links_on_page = get_next_page_links(url)
        dupe_count = 0
        for link in links_on_page:
            full_link = root_url + link
            if full_link not in all_page_links:
                all_page_links.append(full_link)
            else:
                dupe_count += 1
            print(dupe_count)
        if dupe_count < len(links_on_page):
            dupe_count = 0
            url = all_page_links[-1]
        else:
            break
    return all_page_links

def get_site_data():
    site_data_list = []
    total_pages = 11
    starting_page = 1

    while starting_page <= total_pages:
        pages_url = "http://reactwarn.floridajobs.org/WarnList/Records?year=2020&page=" + str(starting_page)
        soup = get_soup(pages_url)
        site_data_list.append(fill_list_rows(soup))
        print(starting_page)
        starting_page += 1

    return site_data_list

def get_soup(url):
    html_content = requests.get(url)
    soup = BeautifulSoup(html_content.text, "html5lib")
    return soup

def create_csv_file():
    with open('FL_WARN_Notice.csv', mode='w+') as csv_file:
        #fieldnames = column_names
        #csv_writer = csv.DictWriter(csv_file, fieldnames)
        #csv_writer.writeheader()
        #csv_writer.writerow({'Company Name' : 'Big Banana Sellers', 'State Notification Date' : '10/19/2020', 'Layoff Date': '11/12/2020', 'Employees Affected' : '99', 'Industry' : 'Banana Farming', 'PDF Link' : 'B-Zone.com'})
        warn_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        warn_writer.writerow(column_names)
        for row in cleaned_rows:
            warn_writer.writerow(row)


raw_list_rows = fill_list_rows(soup)

for row in raw_list_rows:
    cleaned_row = clean_row(row)
    cleaned_rows.append(cleaned_row)

create_csv_file()

#[<td><b>Bloomingdale's The Falls</b> 8778 S.W. 136th StreetMIAMI, FL, 33176</td>, <td>01-07-20</td>, <td>03-07-20<i> thru </i> 03-31-20</td>, <td>146</td>, <td>Retail Trade</td>, <td><a href="/WarnList/Download?file=%5C%5Cdeo-wpdb005%5CReactFiles_P%5CBloomingdale's%20The%20Falls%20-%20Miami.pdf">Download</a></td>]
