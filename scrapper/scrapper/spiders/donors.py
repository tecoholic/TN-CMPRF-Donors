import os
import pandas as pd
import scrapy
import requests
import json

from bs4 import BeautifulSoup

datasets = {}


class DonorsSpider(scrapy.Spider):
    name = "donors"
    allowed_domains = ["ereceipt.tn.gov.in"]

    def get_params_from_soup(self, soup):
        fields = [
            "_TSM_HiddenField_",
            "__EVENTTARGET",
            "__EVENTARGUMENT",
            "__VIEWSTATE",
            "__VIEWSTATEGENERATOR",
            "__VIEWSTATEENCRYPTED",
        ]
        params = {}

        for field in fields:
            el = soup.find(attrs={"name": field})
            if el:
                params[field] = el["value"]
            else:
                params[field] = ""

        return params

    def start_requests(self):
        url = "https://ereceipt.tn.gov.in/cmprf/Interface/CMPRF/MonthWiseReport"
        session = requests.Session()
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        params = self.get_params_from_soup(soup)

        for year in [9, 10]:
            for month in range(1, 13):
                params["ctl00$ContentPlaceHolder1$ddl_paymnet_Mode"] = str(month)
                params["ctl00$ContentPlaceHolder1$ddl_Trans_Status"] = str(year)
                params["ctl00$ContentPlaceHolder1$btnshow"] = "Submit"
                yield scrapy.FormRequest(
                    url=url, formdata=params, cookies=res.cookies.get_dict()
                )
                return

    def get_dataframe(self, response):
        table = response.xpath('//*[@id="ContentPlaceHolder1_grid_View"]').get()
        df = pd.read_html(table)[0]
        df.drop(df.tail(1).index, inplace=True)
        return df

    def parse(self, response):
        title = response.xpath('//*[@id="ContentPlaceHolder1_lblTitle"]/text()').get()
        print(title)
        mselect = response.xpath('//*[@id="ContentPlaceHolder1_ddl_paymnet_Mode"]')
        month = mselect.css("option[selected=selected]::text").get()
        mvalue = mselect.css("option[selected=selected]").attrib["value"]
        yselect = response.xpath('//*[@id="ContentPlaceHolder1_ddl_Trans_Status"]')
        year = yselect.css("option[selected=selected]::text").get()
        yvalue = yselect.css("option[selected=selected]").attrib["value"]

        dkey = f"{year}_{month}"
        print(dkey)
        print(mvalue, yvalue)

        if dkey not in datasets:
            datasets[dkey] = self.get_dataframe(response)
        else:
            datasets[dkey] = datasets[dkey].append(self.get_dataframe(response))

        # check for the next button
        next_btn = response.css("a#ContentPlaceHolder1_grid_View_LinkButton3").get()
        if not next_btn:
            outfile = os.path.join("data", f"{dkey}.csv")
            datasets[dkey].to_csv(outfile, index=False)
            return

        params = self.get_params_from_soup(BeautifulSoup(response.text, "html.parser"))
        params[
            "__EVENTTARGET"
        ] = "ctl00$ContentPlaceHolder1$grid_View$ctl28$LinkButton3"
        params["ctl00$ContentPlaceHolder1$ddl_paymnet_Mode"] = mvalue
        params["ctl00$ContentPlaceHolder1$ddl_Trans_Status"] = yvalue

        print(json.dumps(params, indent=2))

        yield scrapy.FormRequest.from_response(response, formdata=params)
