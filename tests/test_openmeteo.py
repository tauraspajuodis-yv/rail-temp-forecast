import pytest
import requests

from common.weather_api import OpenMeteo

# Reusable constants
LATITUDE = 51.5072
LONGITUDE = 0.1276
START_DATE = '2023-03-20'
DAYS_AHEAD = 1


class TestOpenMeteo:
    @pytest.fixture
    def openMeteo(self):
        return OpenMeteo()

    def testInit(self, openMeteo):
        assert openMeteo.base_url == 'https://api.open-meteo.com/v1/forecast?'

    def testApiUrl(self, openMeteo):
        api_url = openMeteo.generate_api_url(LATITUDE, LONGITUDE,
                                             START_DATE, DAYS_AHEAD)
        assert api_url == 'https://api.open-meteo.com/v1/forecast?' \
            'latitude=51.5072&longitude=0.1276' \
            '&start_date=2023-03-20&end_date=2023-03-21' \
            '&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,' \
            'apparent_temperature,precipitation,cloudcover,cloudcover_low,' \
            'cloudcover_mid,cloudcover_high,shortwave_radiation,' \
            'et0_fao_evapotranspiration,windspeed_10m,direct_radiation,' \
            'diffuse_radiation,direct_normal_irradiance'

    def testApiUrlStatus(self, openMeteo):
        api_url = openMeteo.generate_api_url(LATITUDE, LONGITUDE,
                                             START_DATE, DAYS_AHEAD)
        status_code = requests.get(api_url).status_code
        assert status_code == 200

    def testApiJsonData(self, openMeteo):
        json_data = openMeteo.fetch_api_data(LATITUDE, LONGITUDE,
                                             START_DATE, DAYS_AHEAD)
        assert len(json_data) == 9
        assert list(json_data.keys()) == [
            'latitude', 'longitude', 'generationtime_ms',
            'utc_offset_seconds', 'timezone', 'timezone_abbreviation',
            'elevation', 'hourly_units', 'hourly'
        ]
        assert list(json_data['hourly'].keys()) == [
            'time', 'temperature_2m', 'relativehumidity_2m', 'dewpoint_2m',
            'apparent_temperature', 'precipitation', 'cloudcover',
            'cloudcover_low', 'cloudcover_mid', 'cloudcover_high',
            'shortwave_radiation', 'et0_fao_evapotranspiration',
            'windspeed_10m', 'direct_radiation', 'diffuse_radiation',
            'direct_normal_irradiance'
        ]
        assert len(json_data['hourly']) == 16
        assert len(json_data['hourly']['time']) == 48
        assert len(json_data['hourly']['temperature_2m']) == 48
        assert len(json_data['hourly']['relativehumidity_2m']) == 48

    def testJsonDataProcessing(self, openMeteo):
        json_data = openMeteo.fetch_api_data(LATITUDE, LONGITUDE,
                                             START_DATE, DAYS_AHEAD)
        data_df = openMeteo.add_manual_fields(json_data)
        assert 'month' in list(data_df.columns)
        assert 'day_of_year' in list(data_df.columns)
        assert 'hour_of_day' in list(data_df.columns)
