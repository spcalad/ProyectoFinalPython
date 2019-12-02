# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import folium

def get_table_rows(year):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
            }

    url = f'https://www.procyclingstats.com/race/olympic-games/{year}'
    page = requests.get(url, headers=headers)


    content = page.content.decode("utf-8").replace('</th>', '</td>')
    soup = BeautifulSoup(content, 'html.parser')
    return soup.find_all('tr')
    


def extract_order_row(tableRow, year): 
    datos = tableRow.find_all('td')
    
    if(len(datos) == 0):
        return
    
    #Position
    position = datos[0].get_text()
    
    #Rider
    tmpTeam = datos[1].find_all('span', class_='teammob')[0].text
    rider = datos[1].get_text().replace(tmpTeam, '')
    
    #Age
    age = datos[2].get_text()
    
    #Team
    team = datos[3].get_text()
    
    #Nation
    nation = tableRow.attrs.get('data-nation')
    
    #UCI points
    uciPoints = datos[4].get_text()
    
    return {'year': year,
            'position': position,  
            'rider': rider,
            'age': age,
            'team': team,
            'nation': nation,
            'uciPoints': uciPoints}


def get_results(tableRows, year):
    results = []
    for tableRow in tableRows:
        extractedRow = extract_order_row(tableRow, year)
        if extractedRow != None:
            results.append(extractedRow)
    return results
        



years = ['2000', '2004', '2008', '2012', '2016']
results = []

for year in years:
    tableRows = get_table_rows(years[0])
    results = results + get_results(tableRows, year)
    
##### CONVERT IN DATAFRAME

roadCyclingResults = pd.DataFrame(results)

def cast_to_number(cadena):
    return re.sub(r'[^0-9\.]', '0', str(cadena))

##### CLEAN DATA
    
roadCyclingResults.year = roadCyclingResults.year.astype(int)
roadCyclingResults.position = roadCyclingResults.position.apply(cast_to_number)
roadCyclingResults.position = roadCyclingResults.position.replace('', '0')
roadCyclingResults.position = roadCyclingResults.position.astype(int)
roadCyclingResults.age = roadCyclingResults.age.replace('', '0')
roadCyclingResults.age = roadCyclingResults.age.astype(int)
roadCyclingResults.uciPoints = roadCyclingResults.uciPoints.replace('', '0')
roadCyclingResults.uciPoints = roadCyclingResults.uciPoints.astype(int)



#### DATA ANALYSIS
roadCyclingResults.describe()

out = roadCyclingResults[(roadCyclingResults.age != 0)].age.plot(kind='hist', bins=15)



by_country = roadCyclingResults.groupby('nation').position.count().reset_index()
by_country

# Incializamos el mapa
m = folium.Map(location=[40.42, -3.7], zoom_start=11, tiles='cartodbpositron')

# Add the color for the chloropleth:
folium.Choropleth(
    geo_data='countries.geojson',
    data=by_country,
    columns=['nation', 'position'],
    key_on='feature.properties.ISO_A2',
    fill_color='YlGn'
).add_to(m)

m









#roadCyclingResults.groupby('year').agg({'age': 'mean', 'uciPoints': 'max' })


