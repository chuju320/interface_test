#-*-coding:utf-8-*-
import time
import xlrd
import re

def open_excel(file="case\\test_interface.xls"):
    '''
    打开excel
    :param file:文件
    :return:
    '''
    try:
        f = xlrd.open_workbook(file)
        return f
    except Exception as e:
        print(str(e))

def excel_by_index(sheetName):
    '''
    根据sheet取表
    :param sheetName: sheet页
    :return:
    '''
    f = open_excel()
    sheet = f.sheet_by_name(sheetName)
    return sheet

def getCases():
    '''
    获取cases
    :return:
    '''
    sheet = excel_by_index("CaseInfo")
    case_list = []
    for i in range(1,sheet.nrows):
        row = sheet.row_values(i)
        case_list.append(row)
    return case_list

def getSteps(caseID):
    '''
    根据caseID获取步骤
    :param caseID:
    :return:
    '''
    sheet = excel_by_index("CaseSteps")
    steps_list = []
    for i in range(1,sheet.nrows):
        row = sheet.row_values(i)
        if caseID == row[1]:
            steps_list.append(row)

    return steps_list

def getDatas(caseID):
    '''
    根据caseID和stepID获取请求数据
    :param caseID:
    :param stepID:
    :return:
    '''
    sheet = excel_by_index('CaseDatas')
    data_list = []
    for i in range(1,sheet.nrows):
        row = sheet.row_values(i)
        if row[1] == caseID:
            data_list.append(row)

    return data_list

def getAllDatas():
    '''
    获取所有数据
    :return:
    '''
    sheet = excel_by_index('CaseDatas')
    data_list = []
    for i in range(1,sheet.nrows):
        row = sheet.row_values(i)
        data_list.append(row)
    return data_list

def regularResult(regular,content):
    '''
    匹配正则表达式
    :param regular:
    :return:
    '''
    pattern = re.compile(r"%s"%regular)
    results = pattern.findall(content)   #结果是list
    return results

if __name__ == '__main__':
    sheet = getDatas('vim_01','vim_001')
    print(sheet)