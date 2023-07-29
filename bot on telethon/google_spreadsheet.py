import httplib2
from pprint import pprint
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


class SpreadsheetError(Exception):
    pass


class SpreadsheetNotSetError(SpreadsheetError):
    pass


class SheetNotSetError(SpreadsheetError):
    pass


class Speadsheet:
    def __init__(self, json_creds, debug_mode=False):
        self.debug_mode = debug_mode
        # аутентификация сервисного аккаунта для работы с таблицами
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            json_creds, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        self.auth = self.credentials.authorize(httplib2.Http())
        self.service = build('sheets', 'v4', http=self.auth)
        self.driveService = build('drive', 'v3', http=self.auth)
        self.spreadsheet_id = None
        self.sheet_id = None
        self.sheet_title = None
        self.requests = []
        self.valueRanges = []

    def create(self, title, sheet_title, rows=25, cols=18, locale='ru_RU', timezone='Etc/GMT'):
        spreadsheet = self.service.spreadsheets().create(body={
            'properties': {'title': title, 'locale': locale, 'timeZone': timezone},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': sheet_title,
                                       'gridProperties': {'rowCount': rows, 'columnCount': cols}}}]
        }).execute()
        if self.debug_mode:
            pprint(spreadsheet)
        self.spreadsheet_id = spreadsheet['spreadsheetId']
        self.sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']
        self.sheet_title = spreadsheet['sheets'][0]['properties']['title']

    def share(self, share_request_body):
        if self.spreadsheet_id is None:
            raise SpreadsheetNotSetError()
        if self.driveService is None:
            self.driveService = build('drive', 'v3', http=self.auth)
        share_res = self.driveService.permissions().create(
            fileId=self.spreadsheet_id,
            body=share_request_body,
            fields='id'
        ).execute()
        if self.debug_mode:
            pprint(share_res)

    def share_for_email(self, email):
        self.share({'type': 'user', 'role': 'reader', 'emailAddress': email})

    def share_anybody(self):
        self.share({'type': 'anyone', 'role': 'writer'})

    def get_spreadsheet_id(self):
        if self.spreadsheet_id is None:
            raise SpreadsheetNotSetError()
        return self.spreadsheet_id

    def get_sheet_link(self):
        if self.spreadsheet_id is None:
            raise SpreadsheetNotSetError()
        if self.sheet_id is None:
            raise SheetNotSetError()
        return 'https://docs.google.com/spreadsheets/d/' + self.spreadsheet_id + '/edit#gid=' + str(self.sheet_id)

    def set_spreadsheet_by_id(self, spreadsheet_id):
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        if self.debug_mode:
            pprint(spreadsheet)
        self.spreadsheet_id = spreadsheet['spreadsheetId']
        self.sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']
        self.sheet_title = spreadsheet['sheets'][0]['properties']['title']

    def prepare_addSheet(self, sheet_title, rows=25, cols=18):
        self.requests.append({"addSheet": {
            "properties": {"title": sheet_title, 'gridProperties': {'rowCount': rows, 'columnCount': cols}}}})

    def prepare_setValues(self, cells_range, values, major_dimension="ROWS"):
        self.valueRanges.append(
            {"range": self.sheet_title + "!" + cells_range, "majorDimension": major_dimension, "values": values})

    def runPrepared(self, valueInputOption="USER_ENTERED"):
        if self.spreadsheet_id is None:
            raise SpreadsheetNotSetError()
        upd1Res = {'replies': []}
        upd2Res = {'responses': []}
        try:
            if len(self.requests) > 0:
                upd1Res = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                                  body={"requests": self.requests}).execute()
                if self.debug_mode:
                    pprint(upd1Res)
            if len(self.valueRanges) > 0:
                upd2Res = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                                           body={"valueInputOption": valueInputOption,
                                                                                 "data": self.valueRanges}).execute()
                if self.debug_mode:
                    pprint(upd2Res)
        finally:
            self.requests = []
            self.valueRanges = []
        return (upd1Res['replies'], upd2Res['responses'])

    def addSheet(self, sheet_title, rows=25, cols=18):
        if self.spreadsheet_id is None:
            raise SpreadsheetNotSetError()
        self.prepare_addSheet(sheet_title, rows, cols)
        added_sheet = self.runPrepared()[0][0]['addSheet']['properties']
        self.sheet_id = added_sheet['sheetId']
        self.sheet_title = added_sheet['title']
        return self.sheet_id

    def toGridRange(self, cellsRange):
        if self.sheet_id is None:
            raise SheetNotSetError()
        if isinstance(cellsRange, str):
            startCell, endCell = cellsRange.split(":")[0:2]
            cellsRange = {}
            rangeAZ = range(ord('A'), ord('Z') + 1)
            if ord(startCell[0]) in rangeAZ:
                cellsRange["startColumnIndex"] = ord(startCell[0]) - ord('A')
                startCell = startCell[1:]
            if ord(endCell[0]) in rangeAZ:
                cellsRange["endColumnIndex"] = ord(endCell[0]) - ord('A') + 1
                endCell = endCell[1:]
            if len(startCell) > 0:
                cellsRange["startRowIndex"] = int(startCell) - 1
            if len(endCell) > 0:
                cellsRange["endRowIndex"] = int(endCell)
        cellsRange["sheetId"] = self.sheet_id
        return cellsRange

    def prepare_setDimensionPixelSize(self, dimension, startIndex, endIndex, pixelSize):
        if self.sheet_id is None:
            raise SheetNotSetError()
        self.requests.append({"updateDimensionProperties": {
            "range": {"sheetId": self.sheet_id,
                      "dimension": dimension,
                      "startIndex": startIndex,
                      "endIndex": endIndex},
            "properties": {"pixelSize": pixelSize},
            "fields": "pixelSize"}})

    def prepare_setColumnsWidth(self, startCol, endCol, width):
        self.prepare_setDimensionPixelSize("COLUMNS", startCol, endCol + 1, width)

    def prepare_setColumnWidth(self, col, width):
        self.prepare_setColumnsWidth(col, col, width)

    def prepare_setRowsHeight(self, startRow, endRow, height):
        self.prepare_setDimensionPixelSize("ROWS", startRow, endRow + 1, height)

    def prepare_setRowHeight(self, row, height):
        self.prepare_setRowsHeight(row, row, height)

    def prepare_mergeCells(self, cellsRange, mergeType="MERGE_ALL"):
        self.requests.append({"mergeCells": {"range": self.toGridRange(cellsRange), "mergeType": mergeType}})

    # formatJSON should be dict with userEnteredFormat to be applied to each cell
    def prepare_setCellsFormat(self, cellsRange, formatJSON, fields="userEnteredFormat"):
        self.requests.append({"repeatCell": {"range": self.toGridRange(cellsRange),
                                             "cell": {"userEnteredFormat": formatJSON}, "fields": fields}})

    # formatsJSON should be list of lists of dicts with userEnteredFormat for each cell in each row
    def prepare_setCellsFormats(self, cellsRange, formatsJSON, fields="userEnteredFormat"):
        self.requests.append({"updateCells": {"range": self.toGridRange(cellsRange),
                                              "rows": [{"values": [{"userEnteredFormat": cellFormat} for cellFormat in
                                                                   rowFormats]} for rowFormats in formatsJSON],
                                              "fields": fields}})

