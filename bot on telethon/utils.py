import re
import csv
from PIL import Image, ImageFont, ImageDraw
from google_spreadsheet import Speadsheet
from credentials import creds_json


async def sub_text(nickname, channel, state):
    if state == "ns":
        return str("у @" + nickname + " нет подписки на @" + channel)
    if state == "os":
        return str("у @" + nickname + " есть подписка на @" + channel)
    if state == "es":
        return str("Перепроверьте подписку у @" + nickname + " на @" + channel + " вручную")
    if state == "ex":
        return str("Пользователя @" + nickname + " не существует")


async def find_nickname(msg):
    links = re.findall(r'(https?://\S+)', msg)
    tags = list(filter(lambda word: word[0] == '@', msg.split()))
    nickname = []
    if links:
        for i in links:
            if "https://t.me/" in i:
                nickname.append(i.removeprefix("https://t.me/"))
            if "http://t.me/" in i:
                nickname.append(i.removeprefix("http://t.me/"))
    elif tags:
        for i in tags:
            nickname.append(i.removeprefix("@"))
    else:
        return None
    return nickname


def get_data(spreadsheet_id):
    ss = Speadsheet(creds_json, False)
    ss.set_spreadsheet_by_id(spreadsheet_id)
    ranges = ["total results!C4:G21"]
    results = ss.service.spreadsheets().values().batchGet(spreadsheetId=ss.spreadsheet_id,
                                                          ranges=ranges,
                                                          valueRenderOption='FORMATTED_VALUE',
                                                          dateTimeRenderOption='FORMATTED_STRING').execute()
    sheet_values = results['valueRanges'][0]['values']
    return sheet_values


def get_command(data, count):
    return data[[count][0]]


def table_app(im, font, coordinates_y, column_1, column_2, text, color, count=0, count_2=9):
    draw = ImageDraw.Draw(im)
    for y in coordinates_y:
        data = get_command(text, count)
        #print(text, count)
        data_2 = None
        if count_2 <= len(text) - 1:
            data_2 = get_command(text, count_2)
            count_2 += 1
        count += 1
        count_txt1 = 0
        count_txt2 = 0
        if count_txt1 <= 4:
            for x in column_1:
                draw.text((int(x), int(y)), data[count_txt1], anchor='ms', font=font, fill=color)
                #print(x, y, data[count_txt1])
                count_txt1 += 1
        if count_txt2 <= 4 and count_2 <= len(text) - 1:
            for x in column_2:
                draw.text((int(x), int(y)), data_2[count_txt2], anchor='ms', font=font, fill=color)
                #print(x, y, data[count_txt1])
                count_txt2 += 1
    im.save('test.png')


def get_link_table():
    spreadsheet_id = '1dZcY83ABm7_ndk7tJ - m2Rvt4NrJFFCrOUsSriJdC6r4'
    return 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id


def get_color(template):
    if template == "1":
        return 255
    if template == "2":
        return 255
    if template == "3":
        return 0


def get_column(templates, column):
    if templates == "1":
        if column == 'column_1':
            return ["530", "930", "1045", "1150", "1260"]
        if column == 'column_2':
            return ["1740", "2130", "2245", "2350", "2460"]
        if column == 'column_y':
            return ["460", "575", "685", "790", "900", "1010", "1120", "1230", "1340"]
    if templates == "2":
        if column == 'column_1':
            return ["500", "885", "1015", "1120", "1220"]
        if column == 'column_2':
            return ["1700", "2080", "2205", "2310", "2410"]
        if column == 'column_y':
            return ["540", "645", "755", "850", "950", "1060", "1160", "1260", "1365"]
    if templates == "3":
        if column == 'column_1':
            return ["440", "510", "548", "572", "600"]
        if column == 'column_2':
            return ["720", "795", "830", "855", "880"]
        if column == 'column_y':
            return ["115", "155", "190", "225", "265", "305", "350", "390", "435"]



def get_font_size(template):
    if template == "1":
        return 44
    if template == "2":
        return 44
    if template == "3":
        return 14


async def generate_result(template, config=None):
    filename = 'templates/' + template + '.png'
    with Image.open(filename) as im:
        im.load()
        font = ImageFont.truetype("fonts/firasans/FiraSans-Bold.otf", get_font_size(template))
        text = get_data('1dZcY83ABm7_ndk7tJ-m2Rvt4NrJFFCrOUsSriJdC6r4')
        print(text)
        column_1 = get_column(template, "column_1")
        column_2 = get_column(template, "column_2")
        coordinates_y = get_column(template, "column_y")
        color = get_color(template)
        print(len(text))
        if len(text) > 10:
            table_app(im, font, coordinates_y, column_1, column_2, text, color)


async def result_table(template):
    await generate_result(template)
