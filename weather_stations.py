import datetime
import urllib.request
import urllib.parse
from xml.dom.minidom import parse
import xml.dom.minidom


class WeatherStations:

    def __init__(self):
        self.__last_updated = datetime.datetime.min
        self.__weather_stations = {}
        self.__update()

    def __update(self):
        aviation_stations_url = 'http://opendata.fmi.fi/wfs?request=GetFeature&storedquery_id=fmi::ef::stations&networkid=224&'
        weather_stations_url = 'http://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::ef::stations&networkid=121&'
        '''
        weather_stations_xml = urllib.request.urlopen('http://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::ef::stations&networkid=121&')
        dom_tree = xml.dom.minidom.parse(weather_stations_xml)
        document = dom_tree.documentElement
        elements = document.getElementsByTagName('wfs:member')
        '''

        self.__weather_stations = {}
        self.__last_updated = datetime.datetime.now()
        '''
        for element in elements:
            name = element.getElementsByTagName('ef:name')[0].childNodes[0].data
            fmisid = element.getElementsByTagName('gml:identifier')[0].childNodes[0].data

            split_name = name.split(" ")
            city = split_name[0]
            area = " ".join(split_name[1:])

            if city not in self.__weather_stations:
                self.__weather_stations[city] = []
            self.__weather_stations[city].append([area, fmisid])
        '''
        self.__add_stations(aviation_stations_url)
        self.__add_stations(weather_stations_url)

    def __add_stations(self, url):
        weather_stations_xml = urllib.request.urlopen(url)
        dom_tree = xml.dom.minidom.parse(weather_stations_xml)
        document = dom_tree.documentElement
        elements = document.getElementsByTagName('wfs:member')

        for element in elements:
            name = element.getElementsByTagName('ef:name')[0].childNodes[0].data
            fmisid = element.getElementsByTagName('gml:identifier')[0].childNodes[0].data

            split_name = name.split(" ")
            city = split_name[0]
            area = " ".join(split_name[1:])

            if city not in self.__weather_stations:
                self.__weather_stations[city] = []
            self.__weather_stations[city].append([area, fmisid])


    def print_stations(self):
        if datetime.datetime.now() > self.__last_updated + datetime.timedelta(minutes=10):
            self.__update()
        for city in self.__weather_stations:
            print(city)
            for station in self.__weather_stations[city]:
                print("\tArea: " + station[0] + "\tFMISID: " + str(station[1]))

    def __get_fmisid(self, station_name):
        if datetime.datetime.now() > self.__last_updated + datetime.timedelta(minutes=10):
            self.__update()

        for city in self.__weather_stations:
            
            if station_name == city.lower() and len(self.__weather_stations[city]) == 1:
                return self.__weather_stations[city][0][1]
            elif station_name == city.lower():
                return -1
            for station in self.__weather_stations[city]:
                if station_name == city.lower() + " " + station[0].lower():
                    return station[1]

        for city in self.__weather_stations:
            for station in self.__weather_stations[city]:
                if station_name in station[0].lower():
                    return station[1]
        return -1

    def __get_with_place(self, place):
        values = []
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
        start_time_stamp = start_time.strftime("%Y-%m-%dT%H:%M:00Z")

        url = 'http://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::observations::weather::simple&place=' + \
              urllib.parse.quote(place) + '&starttime=' + start_time_stamp + '&parameters=t2m,rh,td,ws_10min,wd_10min&'

        weather_xml = urllib.request.urlopen(url)
        dom_tree = xml.dom.minidom.parse(weather_xml)
        document = dom_tree.documentElement
        elements = document.getElementsByTagName('wfs:member')[-5:]
        for element in elements:
            # type = element.getElementsByTagName('BsWfs:ParameterName')[0].childNodes[0].data
            value = element.getElementsByTagName('BsWfs:ParameterValue')[0].childNodes[0].data
            values.append(value)
            # print('Type: %s Value: %s' % (type.childNodes[0].data, value.childNodes[0].data))
        return WeatherReport(values)

    def __get_with_fmisid(self, fmisid):
        values = []
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
        start_time_stamp = start_time.strftime("%Y-%m-%dT%H:%M:00Z")

        url = 'http://opendata.fmi.fi/wfs?request=getFeature&storedquery_id=fmi::observations::weather::simple&fmisid=' + \
              fmisid + '&starttime=' + start_time_stamp + '&parameters=t2m,rh,td,ws_10min,wd_10min&'

        weather_xml = urllib.request.urlopen(url)
        dom_tree = xml.dom.minidom.parse(weather_xml)
        document = dom_tree.documentElement
        elements = document.getElementsByTagName('wfs:member')[-5:]
        for element in elements:
            type = element.getElementsByTagName('BsWfs:ParameterName')[0].childNodes[0].data
            value = element.getElementsByTagName('BsWfs:ParameterValue')[0].childNodes[0].data
            values.append(value)
            # print('Type: %s Value: %s' % (type.childNodes[0].data, value.childNodes[0].data))
        return WeatherReport(values)

    def get_weather(self, station_name):
        station_name_lower = station_name.lower().strip()
        fmisid = self.__get_fmisid(station_name_lower)
        if fmisid == -1:
            return self.__get_with_place(station_name_lower)
        else:
            return self.__get_with_fmisid(fmisid)

    def get_stations(self, search):
        response = []
        search_lower = search.lower().strip()
        if datetime.datetime.now() > self.__last_updated + datetime.timedelta(minutes=10):
            self.__update()
        for city, area in self.__weather_stations.items():
            if city.lower() == search_lower:
                for station in self.__weather_stations[city]:
                    response.append(station[0])
                return response
        return response


class WeatherReport:

    def __init__(self, values):
        self.temperature = values[0]
        self.humidity = values[1]
        self.dew_point = values[2]
        self.wind_speed = values[3]
        self.wind_direction = values[4]

    def has_wind(self):
        return "NaN" not in self.wind_speed
