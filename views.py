from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import requests
import json
import time
from googlesearch import search
import urllib.parse

views = Blueprint(__name__, "views")

load_dotenv()

def get_numbers(w):
    nums = ""
    for c in w:
        if (c.isnumeric()):
                nums += c
    return (w if nums == "" else int(nums))
options = Options()
options.add_argument("-headless")
driver = webdriver.Firefox(options=options)

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/airbnb-API")
def airbnb():
    listing_url = None
    try:
        listing_url = request.args.get("url")
    except:
        return {'Error' : 'URL argument not provided'},200
    listing_url = urllib.parse.unquote(listing_url)
    driver.get(listing_url)
    time.sleep(5)
    try:
        airbnb_name = driver.find_element("class name","hpipapi").get_attribute("innerHTML")
        airbnb_pic = driver.find_element("class name","itu7ddv").get_attribute("src")
        info = driver.find_element("class name","lgx66tx").text.split("·")
        title = get_numbers(driver.find_element("class name", "hpipapi").text)
    except:
        return {'Error' : 'Unable to read Airbnb webpage'}, 200
    price = None
    map_link, scroll_down_height = None, 0
    while not map_link:
        try:
            map_link = driver.find_element("xpath","/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[5]/div/div/div/div[2]/section/div[3]/div[4]/div[2]/div/div/div[16]/div/div[5]/div[2]/a").get_attribute("href")
            price = get_numbers(driver.find_elements("class name", "_tyxjp1")[1].text.strip())
        except:
            scroll_down_height += 20
            driver.execute_script("window.scroll(0, " + str(scroll_down_height) + ");")
    info = [x.strip() for x in info]
    num_guests, num_br, num_bed = (get_numbers(x) for x in info[0:3])
    num_bath = int(np.ceil(float(info[3].split()[0])))
    lat, lng, spec_char_count = "", "", 0
    for c in map_link:
        if(c == "@" or c == ","):
            spec_char_count += 1
        elif(spec_char_count == 1):
            lat += c
        elif(spec_char_count == 2):
            lng += c
        elif(spec_char_count == 3):
            break
    price_per_night = "$" + str(price) + " per night"
    bed_and_bath = str(num_br) + (" Bedroom, " if num_br == 1 else (" Bedrooms, " if isinstance(num_br,int) else ", ")) + str(num_bath) + (" Bathroom" if num_bath == 1 else " Bathrooms")
    try:
        loc_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?f=pjson&location=" + lng + "," + lat + "&token=" + os.getenv("API_TOKEN")
        response = requests.get(loc_url)
        address_json = response.json()
        add_num = address_json["address"]["AddNum"]
        street = (address_json["address"]["Address"] if add_num == "" else address_json["address"]["Address"][(len(add_num) + 1):])
        city = address_json["address"]["City"]
        state = address_json["address"]["RegionAbbr"]
        zipcode = address_json["address"]["Postal"]
        street_address = ((street + ", ") if street != "" else "") + city + ", " + state + " " + zipcode
        address = street_address if add_num == "" else add_num + " " + street_address
        zillow_link = [_ for _ in search(address + " zillow", num_results=1)][0]
        driver.get(zillow_link)
        rent_est = None
    except:
        return {'Error' : 'Unable to estimate address'}, 200
    try:
        if (driver.find_elements("class name", "Text-c11n-8-89-0__sc-aiai24-0.UtIzR")[3].text == address):
            rent_est = get_numbers(driver.find_elements("class name","Text-c11n-8-89-0__sc-aiai24-0.cfmKEe")[1].text)
    except:
        try:
            redfin_link = [_ for _ in search(address + " redfin", num_results=1)][0]
            driver.get(redfin_link)
            redfin_address = driver.find_element("class name", "street-address").text + " " + driver.find_element("class name", "dp-subtext.bp-cityStateZip").text
            if(redfin_address == address):
                rent_est = get_numbers(driver.find_elements("class name", "price")[1].text)
        except:
            pass
    if (not rent_est or not isinstance(rent_est,int)):
        driver.get("https://app.rentcast.io/app")
        elems = {"Text":[], "Element":[]}
        for elem in driver.find_elements("class name", "dropdown-item"):
            elems[elem.get_attribute("textContent")] = elem
        driver.find_element("class name", "form-control").send_keys(address)
        driver.find_elements("class name", "dropdown-toggle")[3].click()
        elems[" Apartment "].click()
        driver.find_elements("class name", "dropdown-toggle")[4].click()
        bedrooms = ""
        elems[" " + (((str(num_br) if num_br < 6 else "6+") + (" Bed" if num_br == 1 else " Beds")) if isinstance(num_br, int) else num_br) + " "].click()
        driver.find_elements("class name", "dropdown-toggle")[5].click()
        elems[" " + (str(num_bath) if num_bath < 4 else "4+") + (" Bath" if num_bath == 1 else " Baths") + " "].click()
        driver.find_element("class name", "btn-primary").click()
        time.sleep(3)
        test_addresses = []
        if (add_num != ""):
            for i in range(4):
                x = int(np.ceil((i+1)/2) * pow(-1,i))
                new_add_num = int(add_num) + x
                test_addresses.append(str(new_add_num) + " " + street_address)
        test_addresses.append(street_address)
        test_addresses.append(city + ", " + state + " " + zipcode)
        for test_address in test_addresses:
            if (rent_est):
                break
            try:
                rent_est = get_numbers(driver.find_element("class name", "display-3").get_attribute("textContent"))
            except:
                driver.find_element("class name", "form-control").clear()
                driver.find_element("class name", "form-control").send_keys(test_address)
                driver.find_element("class name", "btn-primary").click()
                time.sleep(len(test_addresses) + 2)
        remote_location = False
        if (not rent_est):
            state_rent_data = pd.read_csv("state_rent_data.csv")
            try:
                rent_est = round(state_rent_data.loc[state_rent_data["state"] == address_json["address"]["Region"]].iloc[0,1] * (num_br + num_bath / 3))
            except:
                return {'Airbnb link' : listing_url, 'Airbnb name' : airbnb_name, 'Airbnb picture' : airbnb_pic, 'approximate address' : address, 'stay price' : price, 'Error' : 'Rent estimate could not calculated: location may not be in the US'}
            remote_location = True
    utl_avg = 429.33 # from https://www.forbes.com/home-improvement/living/monthly-utility-costs-by-state/
    day_rent_est = round(((rent_est + utl_avg) * 12 / 365.25),2)
    profit_margin = round(100 * (price - day_rent_est) / price,2)
    premium_perc = round(price/day_rent_est * 100)
    host_profit = round(price - day_rent_est,2)
    return {'Airbnb link' : listing_url, 'Airbnb name' : airbnb_name, 'Airbnb picture' : airbnb_pic, 'approximate address' : address, 'stay price' : price, 'daily host cost' : day_rent_est, 'premium percentage' : premium_perc, 'occupied profit margin' : profit_margin, 'occupied daily profit' : host_profit}
