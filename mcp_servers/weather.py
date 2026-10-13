# import requests
# from mcp.server.fastmcp import FastMCP

# import config


# mcp = FastMCP("Weather_MCP_Server", port=8002)


# FORECAST_API_URL = (
#     "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073"
# )
# WARNING_API_URL = (
#     "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-001"
# )
# WIND_API_URL = (
#     "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
# )
# RAINY_API_URL = (
#     "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
# )


# def format_rainfall(value):
#     if value == "T":
#         return "雨跡"
#     if value in {"X", "-99", -99}:
#         return None
#     if value in {"-98", -98}:
#         return "連續 6 小時無降水"
#     return f"{value} mm"

# @mcp.tool()
# def get_weather() -> dict:
#     """查詢天氣"""
#     location_name = "霧峰區"

#     forecast_response = requests.get(
#         FORECAST_API_URL,
#         params={
#             "Authorization": config.WEATHER_API_KEY,
#             "LocationName": location_name,
#             "ElementName": (
#                 "天氣預報綜合描述,3小時降雨機率,溫度,"
#                 "天氣現象,體感溫度"
#             ),
#         },
#     )
#     forecast_data = forecast_response.json()

#     warning_response = requests.get(
#         WARNING_API_URL,
#         params={
#             "Authorization": config.WEATHER_API_KEY,
#             "parameter": "alert_title",
#             "areaDesc": "臺中市",
#             "expires": "",
#             "description": "typhoon-info",
#         },
#     )
#     warning_data = warning_response.json()

#     wind_response = requests.get(
#         WIND_API_URL,
#         params={
#             "Authorization": config.WEATHER_API_KEY,
#             "StationId": "G2F820",
#             "WeatherElement": "WindSpeed,GustInfo",
#             "GeoInfo": "TownName",
#         },
#     )
#     wind_data = wind_response.json()

#     rainfall_response = requests.get(
#         RAINY_API_URL,
#         params={
#             "Authorization": config.WEATHER_API_KEY,
#             "StationId": "G2F820",
#             "RainfallElement": "Past1hr,Past3hr,Past24hr",
#             "GeoInfo": "TownName",
#         },
#     )
#     rainfall_data = rainfall_response.json()

#     location_data = forecast_data["records"]["Locations"][0]["Location"][0]
#     weather_elements = location_data["WeatherElement"]

#     parsed_data = {}
#     time_info = {}

#     for item in weather_elements:
#         element_name = item["ElementName"]
#         first_record = item["Time"][0]
#         value = list(first_record["ElementValue"][0].values())[0]
#         parsed_data[element_name] = value

#         if element_name == "天氣預報綜合描述":
#             time_info["StartTime"] = first_record["StartTime"]
#             time_info["EndTime"] = first_record["EndTime"]

#     wind_elements = wind_data["records"]["Station"][0]["WeatherElement"]
#     wind_speed = wind_elements["WindSpeed"]
#     peak_gust_speed = wind_elements["GustInfo"]["PeakGustSpeed"]

#     rainfall_station = rainfall_data["records"]["Station"][0]
#     rainfall_elements = rainfall_station["RainfallElement"]
#     past_1hr_rainfall = rainfall_elements["Past1hr"]["Precipitation"]
#     past_3hr_rainfall = rainfall_elements["Past3hr"]["Precipitation"]
#     past_24hr_rainfall = rainfall_elements["Past24hr"]["Precipitation"]

#     warnings = []
#     for warning in warning_data["records"].get("info", []):
#         headline = warning.get("headline")
#         typhoon_sections = warning["description"]["typhoon-info"][0]["section"]
#         typhoon_info = next(
#             section
#             for section in typhoon_sections
#             if section["title"] == "颱風資訊"
#         )
#         area_desc = [area["areaDesc"] for area in warning.get("area", [])]
#         warnings.append(
#             {
#                 "headline": headline,
#                 "cwa_typhoon_name": typhoon_info["cwa_typhoon_name"],
#                 "areaDesc": area_desc,
#             }
#         )

#     result = {
#         "location": location_name,
#         "time": f"{time_info['StartTime']} ~ {time_info['EndTime']}",
#         "溫度": parsed_data["溫度"],
#         "體感溫度": parsed_data["體感溫度"],
#         "降雨機率": parsed_data["3小時降雨機率"],
#         "天氣現象": parsed_data["天氣現象"],
#         "1小時累積雨量": format_rainfall(past_1hr_rainfall),
#         "3小時累積雨量": format_rainfall(past_3hr_rainfall),
#         "24小時累積雨量": format_rainfall(past_24hr_rainfall),
#         "風速": f"{wind_speed} m/s",
#         "最大瞬間陣風": f"{peak_gust_speed} m/s",
#         "警報": warnings,
#     }
#     return result


# if __name__ == "__main__":
#     mcp.run(transport="streamable-http")

import requests
import config
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather_MCP_Server", port=8002)

#霧峰一週氣象觀測
WUFENG_WEEK_OBSERVATION_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-075"
#颱風警報
TYPHOON_WARNING_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0034-001"
#霧峰雨量觀測 1、3、24小時累計雨量
WUFENG_RAIN_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
#當日氣溫與風速
WUFENG_TODAY_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"


def format_rainfall(value):
    if value == "T":
        return "雨跡"
    if value in {"X", "-99", -99}:
        return None
    if value in {"-98", -98}:
        return "連續 6 小時無降水"
    return f"{value} mm"


def parse_weather_data(forecast_data: dict, warning_data: dict, rain_data: dict, today_data:dict) -> dict:
    """整理一週氣象、紫外線、颱風警報與目前雨量。"""
    location = forecast_data["records"]["Locations"][0]["Location"][0]
    elements = {}
    for element in location["WeatherElement"]:
        elements[element["ElementName"]] = element["Time"]

    max_times = elements["最高溫度"]
    min_times = elements["最低溫度"]
    description_times = elements["天氣預報綜合描述"]
    forecast = []
    for time_index in range(1, 14, 2):
        max_period = max_times[time_index]
        min_period = min_times[time_index]
        description_period = description_times[time_index]
        start_time = max_period["StartTime"]
        end_time = max_period["EndTime"]

        forecast.append({
            "開始觀測時間": start_time,
            "結束觀測時間": end_time,
            "最高溫度": max_period["ElementValue"][0]["MaxTemperature"],
            "最低溫度": min_period["ElementValue"][0]["MinTemperature"],
            "天氣現象描述": description_period["ElementValue"][0]["WeatherDescription"],
        })

    uv_result = []
    for uv_period in elements["紫外線指數"]:
        uv_result.append({
            "開始觀測時間": uv_period["StartTime"],
            "結束觀測時間": uv_period["EndTime"],
            "紫外線指數": uv_period["ElementValue"][0]["UVIndex"],
        })

    warnings = []
    for info in warning_data["records"].get("info"):
        headline = info.get("headline")
        if headline:
            warnings.append(headline)

    rainfall = []
    for station in rain_data["records"].get("Station"):
        rain = station["RainfallElement"]
        rainfall.append({
            "觀測時間": station["ObsTime"]["DateTime"],
            "過去1小時累計雨量": format_rainfall(rain["Past1hr"]["Precipitation"]),
            "過去3小時累計雨量": format_rainfall(rain["Past3hr"]["Precipitation"]),
            "過去24小時累計雨量": format_rainfall(rain["Past24hr"]["Precipitation"]),
        })


    today_weather_data = []
    for today in today_data["records"].get("Station"):
        today_weather = today["WeatherElement"]
        today_weather_data.append({
            "風速":f"{today_weather["WindSpeed"]} m/s",
            "現在溫度":today_weather["AirTemperature"]
        })

    result = {
        "一週氣象觀測": forecast,
        "一週紫外線資料": uv_result,
        "颱風警報狀態": warnings,
        "目前雨量觀測": rainfall,
        "今日天氣":today_weather_data
    }
    return result


@mcp.tool()
def get_weather() -> dict:
    """查詢霧峰區一週天氣、雨量、當日氣象和胎風警報"""

    location_name = "霧峰區"

    #一週觀測資料
    forecast_response = requests.get(
        WUFENG_WEEK_OBSERVATION_API,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "LocationName": location_name,
            "ElementName": "最高溫度,最低溫度,天氣預報綜合描述,紫外線指數",
        },
        timeout=20,
    )
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    #颱風警報
    warning_response = requests.get(
        TYPHOON_WARNING_API,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "info": "headline",
            "areaDesc": "臺中市",
        },
        timeout=20,
    )
    warning_response.raise_for_status()
    warning_data = warning_response.json()

    #雨量資料
    rain_response = requests.get(
        WUFENG_RAIN_API,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "StationName": "霧峰",
            "RainfallElement": "Past1hr,Past3hr,Past24hr",
            "GeoInfo":"TownName"
        },
        timeout=20,
        )
    rain_response.raise_for_status()
    rain_response_data = rain_response.json()

    #今日溫度資料
    today_response = requests.get(
        WUFENG_TODAY_API,
        params={
            "Authorization": config.WEATHER_API_KEY,
            "StationName": "農業試驗所",
            "WeatherElement": "WindSpeed,AirTemperature",
            "GeoInfo":"TownName"
        },
        timeout=20,
    )

    today_response.raise_for_status()
    today_response_data = today_response.json()

    return parse_weather_data(forecast_data, warning_data, rain_response_data,today_response_data)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

