import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


class DonorScrapper(object):
    def __init__(self):
        self.start_url = (
            "https://ereceipt.tn.gov.in/cmprf/Interface/CMPRF/MonthWiseReport"
        )
        self.browser = webdriver.Chrome()

    def start(self):
        self.browser.get(self.start_url)
        for year in ["2020"]:
            for i in range(1, 13):
                year_select = Select(
                    self.browser.find_element_by_name(
                        "ctl00$ContentPlaceHolder1$ddl_Trans_Status"
                    )
                )
                year_select.select_by_visible_text(year)
                if year == "2020" and i not in [3, 4]:
                    continue
                month = Select(
                    self.browser.find_element_by_name(
                        "ctl00$ContentPlaceHolder1$ddl_paymnet_Mode"
                    )
                )
                month.select_by_value(str(i))
                submit_btn = self.browser.find_element_by_name(
                    "ctl00$ContentPlaceHolder1$btnshow"
                )
                submit_btn.click()
                self.scrape_pages(int(year), i)
                self.browser.get("https://google.com")
                self.browser.get(self.start_url)
        self.browser.close()

    def scrape_pages(self, year, month):
        print(f"Scrapping details for year: {year} month: {month}")
        outfile = os.path.join("data", f"{year}_{month}.csv")

        table_element = self.browser.find_element_by_id("ContentPlaceHolder1_grid_View")
        main = pd.read_html(table_element.get_attribute("outerHTML"))[0]
        main.drop(main.tail(1).index, inplace=True)

        try:
            next_btn = self.browser.find_element_by_id(
                "ContentPlaceHolder1_grid_View_LinkButton3"
            )
            while next_btn:
                next_btn.click()
                table_element = self.browser.find_element_by_id(
                    "ContentPlaceHolder1_grid_View"
                )
                df = pd.read_html(table_element.get_attribute("outerHTML"))[0]
                df.drop(df.tail(1).index, inplace=True)
                main = main.append(df)
                next_btn = self.browser.find_element_by_id(
                    "ContentPlaceHolder1_grid_View_LinkButton3"
                )
        except NoSuchElementException:
            # all pages done
            main.to_csv(outfile, index=False)


if __name__ == "__main__":
    scrapper = DonorScrapper()
    scrapper.start()
