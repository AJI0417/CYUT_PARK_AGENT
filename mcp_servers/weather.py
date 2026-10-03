import requests
from mcp.server.fastmcp import FastMCP

import config


mcp = FastMCP("Weather_MCP_Server", port=8002)


FORECAST_API_URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073"
)
WARNING_API_URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-001"
)
WIND_API_URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
)
RAINY_API_URL = (
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
)


def format_rainfall(value):
    if value == "T":
        return "雨跡"
    if value in {"X", "-99", -99}:
        return None
    if value in {"-98", -98}:
        return "連續 6 小時無降水"
    return f"{value} mm"

@mcp.tool()
def get_weather() -> dict:
    """查詢天氣"""
    location_name = "霧峰區"

    forecast_response = requests.get(
        FORECAST_API_URL,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "LocationName": location_name,
            "ElementName": (
                "天氣預報綜合描述,3小時降雨機率,溫度,"
                "天氣現象,體感溫度"
            ),
        },
    )
    forecast_data = forecast_response.json()

    warning_response = requests.get(
        WARNING_API_URL,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "parameter": "alert_title",
            "areaDesc": "臺中市",
            "expires": "",
            "description": "typhoon-info",
        },
    )
    warning_data = warning_response.json()

    wind_response = requests.get(
        WIND_API_URL,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "StationId": "G2F820",
            "WeatherElement": "WindSpeed,GustInfo",
            "GeoInfo": "TownName",
        },
    )
    wind_data = wind_response.json()

    rainfall_response = requests.get(
        RAINY_API_URL,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "StationId": "G2F820",
            "RainfallElement": "Past1hr,Past3hr,Past24hr",
            "GeoInfo": "TownName",
        },
    )
    rainfall_data = rainfall_response.json()

    location_data = forecast_data["records"]["Locations"][0]["Location"][0]
    weather_elements = location_data["WeatherElement"]

    parsed_data = {}
    time_info = {}

    for item in weather_elements:
        element_name = item["ElementName"]
        first_record = item["Time"][0]
        value = list(first_record["ElementValue"][0].values())[0]
        parsed_data[element_name] = value

        if element_name == "天氣預報綜合描述":
            time_info["StartTime"] = first_record["StartTime"]
            time_info["EndTime"] = first_record["EndTime"]

    wind_elements = wind_data["records"]["Station"][0]["WeatherElement"]
    wind_speed = wind_elements["WindSpeed"]
    peak_gust_speed = wind_elements["GustInfo"]["PeakGustSpeed"]

    rainfall_station = rainfall_data["records"]["Station"][0]
    rainfall_elements = rainfall_station["RainfallElement"]
    past_1hr_rainfall = rainfall_elements["Past1hr"]["Precipitation"]
    past_3hr_rainfall = rainfall_elements["Past3hr"]["Precipitation"]
    past_24hr_rainfall = rainfall_elements["Past24hr"]["Precipitation"]

    warnings = []
    for warning in warning_data["records"].get("info", []):
        headline = warning.get("headline")
        typhoon_sections = warning["description"]["typhoon-info"][0]["section"]
        typhoon_info = next(
            section
            for section in typhoon_sections
            if section["title"] == "颱風資訊"
        )
        area_desc = [area["areaDesc"] for area in warning.get("area", [])]
        warnings.append(
            {
                "headline": headline,
                "cwa_typhoon_name": typhoon_info["cwa_typhoon_name"],
                "areaDesc": area_desc,
            }
        )

    result = {
        "location": location_name,
        "time": f"{time_info['StartTime']} ~ {time_info['EndTime']}",
        "溫度": parsed_data["溫度"],
        "體感溫度": parsed_data["體感溫度"],
        "降雨機率": parsed_data["3小時降雨機率"],
        "天氣現象": parsed_data["天氣現象"],
        "1小時累積雨量": format_rainfall(past_1hr_rainfall),
        "3小時累積雨量": format_rainfall(past_3hr_rainfall),
        "24小時累積雨量": format_rainfall(past_24hr_rainfall),
        "風速": f"{wind_speed} m/s",
        "最大瞬間陣風": f"{peak_gust_speed} m/s",
        "警報": warnings,
    }
    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
