# coding=utf-8
import requests
import demjson
from bs4 import BeautifulSoup as bs
import re

numbersOption = []
forwardOption = {}
stopOption = {}


# 查询线路
def getNumbers(number):
    global numbersOption
    # numbersOption.clear()
    del numbersOption[:]
    numberStr = str(number)
    requestNumbersUrl = 'https://www.bjbus.com/home/index.php'
    responseNumbers = requests.get(requestNumbersUrl)
    responseNumbers.encoding = 'utf-8'
    numberHtml = bs(responseNumbers.text, 'html.parser')
    numbersOptionHtml = numberHtml.find(id='selBLine').findAll('a')

    for item in numbersOptionHtml:
        if len(numberStr) < 1:
            print(item.text)
            numbersOption.append(item.text)
        else:
            if numberStr in item.text:
                print(item.text)
                numbersOption.append(item.text)

    re_digits = re.compile(r'(\d+)')

    def emb_numbers(s):
        pieces = re_digits.split(s)
        pieces[1::2] = map(int, pieces[1::2])
        return pieces

    return sorted(numbersOption, key=emb_numbers)


# 获取某一线路的两个方向描述及id
def getForward(number):
    global forwardOption
    forwardOption.clear()
    # 获取线路的两个方向
    requestForwardUrl = 'http://www.bjbus.com/home/ajax_rtbus_data.php?act=getLineDirOption&selBLine=' + number
    responseForward = requests.get(requestForwardUrl)
    responseForward.encoding = 'utf-8'
    print(responseForward.text)
    forwardHtml = bs(responseForward.text, 'html.parser')
    forwardOptionsHtml = forwardHtml.find_all('option')
    for item in forwardOptionsHtml:
        if len(item.attrs['value']) > 0:
            forwardValue = item.attrs['value']
            forwardName = item.string
            forwardOption[item.attrs['value']] = forwardName
            print("查询到的线路方向:", forwardValue, " ", forwardName)

    return forwardOption


# 获取某一线路的其中一个方向的所有站点名称及id
def getStopName(number, forward):
    global stopOption
    stopOption.clear()
    requestStopUrl = "http://www.bjbus.com/home/ajax_rtbus_data.php?act=getDirStationOption&selBLine=" + number + "&selBDir=" + forward
    responseStop = requests.get(requestStopUrl)
    responseStop.encoding = 'utf-8'
    print(responseStop.text)
    stopHtml = bs(responseStop.text, 'html.parser')
    stopOptionsHtml = stopHtml.find_all('option')
    for item in stopOptionsHtml:
        if len(item.attrs['value']) > 0:
            stopValue = item.attrs['value']
            stopName = item.string
            stopOption[item.attrs['value']] = stopName
            print("查询到的车站:", stopValue, " ", stopName)
    return stopOption


# 获取某一线路的其中一个方向中某一站点的公交车位置实时信息
def getGpsInfo(number, forward, stop):
    requestUrl = "http://www.bjbus.com/home/ajax_rtbus_data.php?act=busTime&selBLine=" + number + "&selBDir=" + forward + "&selBStop=" + stop
    # requestUrl = f'http://www.bjbus.com/home/ajax_rtbus_data.php?act=busTime&selBLine={number}&selBDir={forward}&selBStop={stop}'
    response = requests.get(requestUrl)
    response.encoding = 'utf-8'
    resultHtml = demjson.decode(response.text)
    # 解析到站信息
    info = {}  # 保存解析后的站点信息

    infoHtml = bs(resultHtml['html'], 'html.parser')

    info['line'] = infoHtml.find(id='lh').text
    info['forwards'] = infoHtml.find(id='lm').text

    yunyingInfo = infoHtml.find('p').text
    yunyingInfo = "".join(yunyingInfo.split())
    info['lineinfo'] = yunyingInfo

    daozhanInfo = infoHtml.find('div').find('p').findNext().text
    info['gpsinfo'] = daozhanInfo

    for key, value in info.items():
        print(key, value)

    titles = infoHtml.findAll("span", attrs={"title": True})
    id = 1
    stops = []
    for item in titles:
        title = item.text
        stop = {'id': id, 'title': title}
        stops.append(stop)
        id = id + 1
    info['stops'] = stops

    count = 0
    stations = infoHtml.find(id='cc_stop').find('ul').findAll('li')
    # busc为未到站 clstag是据站点的距离（米）
    comings = []
    arrived = []
    for station in stations:
        if station.find(class_='busc') is not None:
            count = count + 1
            id = int((station.div['id'])[:-1])
            distance = station.i['clstag']
            print("途中id", id, stops[id - 1])
            print("距离", distance, "米")
            carComing = {'id': id, 'distance': distance}
            comings.append(carComing)
        if station.find(class_='buss') is not None:
            id = int(station.div['id'])
            print("到站id", id, stops[id - id])
            count = count + 1
            carArrived = {'id': id}
            arrived.append(carArrived)
    info['comings'] = comings
    info['arrived'] = arrived
    info['totalcars'] = count
    print("总车辆：", count)

    return info
