#-*-coding:utf-8-*-
import requests
import unittest
import basePage
#import queue
import json
import HTMLTestRunner3
import pprint

class Cases(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = requests.session()
        cls.params = {}

    def setUp(self):
        pass

    def action(self,case,steps,datas):
        '''
        执行
        :param case:用例
        :param steps:步骤
        :param datas:数据
        :return:
        '''
        caseID = case[0]  #用例id
        caseName = case[1] #用例名称
        caseSummary = case[2] #用例主题
        caseUrl = case[3]  #url
        caseCode = case[4] #编码格式
        caseAuth = case[5]  #认证
        caseMD = case[6]   #数据格式：SSl,CERT,DATA
        caseIniData = case[7]  #初始化参数
        self.setInitData(caseMD,caseIniData)
        k = 2
        if caseAuth:
            jsonData = json.loads(caseAuth)
            self.session.auth = (jsonData['username'],jsonData['password'])
        print('执行用例{id}:{name}'.format(id=caseID,name=caseName))
        for step in steps:
            stepID = step[0]  #步骤id
            stepPro = step[2]  #http、https
            stepSummary = step[3]    #步骤主题
            stepURI = step[4]   #URI
            stepHeader = json.loads(step[5])   #header
            stepMethod = step[6]  #method
            stepDataType = step[7]     #请求数据格式
            stepGetValue = step[8]  #获取的值
            stepVari = step[9]    #设置变量
            stepPoint = step[10]   #断言方式
            stepAssert = step[11]   #断言对象
            stepExcept = step[12]   #期望值
            print('执行步骤{id}:{name}'.format(id=caseID,name=caseName))
            stepURI = self.getVari(stepURI)
            self.url = stepPro + '://' + caseUrl + stepURI
            self.session.headers.update(stepHeader)
            res = self.requestTo(stepMethod,stepDataType,datas[k])
            #设置编码
            if caseCode:
                res.encoding == caseCode
            #设置变量，提取数据
            if str(stepGetValue).strip() or str(stepVari).strip():
                if str(stepVari).startswith("${"):
                    jsons = res.json()
                    value = jsons.get(stepGetValue, '')
                    self.params[stepVari] = value
                else:
                    print('自定义变量失败！格式不正确：{}'.format(stepVari))
            self.assertData(res,stepAssert,stepPoint,stepExcept,stepVari)
            k += 1

    def requestTo(self,stepMethod,dataType,datas):
        '''
        发送请求
        :param dataType:
        :param data:
        :return:
        '''
        data = self.getVari(datas) if datas else ''
        self.print_start(self.session.headers, stepMethod, data)
        if dataType == 'File':
            with open(data) as f:
                res = self.session.post(self.url,data=f)
            return res
        try:
            if stepMethod == 'GET':
                res = self.session.get(self.url, params=data, hooks=dict(response=self.responseInfo))
            elif stepMethod == 'POST':
                res = self.session.post(self.url, data=data, hooks=dict(response=self.responseInfo))
            elif stepMethod == 'PUT':
                res = self.session.put(self.url, data=data, hooks=dict(response=self.responseInfo))
            elif stepMethod == 'DELETE':
                res = self.session.delete(self.url)
            else:
                print('Method {} 无效！'.format(stepMethod))
                raise ('method 无效!')
            return res
        except Exception as e:
            print('server not good')
            raise (e)

    def print_start(self,headers,method,data):
        '''
        在请求之前打印信息
        :param headers:
        :param data:
        :return:
        '''
        print()
        print(method, ":", self.url)
        print('Request Headers:')
        print('User-Agent:',headers.get('User-Agent',''))
        print('Accept-Encoding:',headers.get('Accept-Encoding',''))
        print('Accept:',headers.get('Accept',''))
        print('Connection:',headers.get('Connection',''))
        print('content-type:',headers.get('content-type',''))
        print('Data:')
        pprint.pprint(data)

    def responseInfo(self,response,*args,**kwargs):
        '''
        打印响应值信息
        :param response:
        :return:
        '''
        if response:
            print('')
            print('time:',response.elapsed)
            print('Response Code:',response.status_code)
            print('Response Headers:')
            print('Content-Length:',response.headers.get('Content-Length',''))
            print('Content-Type:',response.headers.get('Content-Type',''))
            print('Response:')
            pprint.pprint(response.text)

    def setInitData(self,type,data):
        '''
        初始化数据
        :param data:
        :return:
        '''
        if data:
            if type == 'SSL':
                self.session.verify = data
            elif type == 'CERT':
                self.session.cert = data
            else:
                try:
                    data = json.loads(data)
                    self.params.update(data)
                except Exception as e:
                    print('初始化数据失败，请检查数据格式：{}'.format(data))

    def getVari(self,data):
        '''
        还原变量值
        :param data:
        :return:
        '''
        data = str(data)
        if '${' in data:
            for key in self.params.keys():
                if key in data:
                    data = data.replace(key,self.params[key])
        return data

    def assertData(self,res,assertType,point,excepts,variable=None):
        '''
        断言
        :param res: 响应值
        :param assertType: 断言方式
        :param point: 断言目标
        :param excepts: 期望值
        :param variable: 当前步骤的变量
        :return:
        '''
        if point == 'CODE':
            response = str(res.status_code)
            excepts = str(int(excepts))
        elif point == 'JSON':
            response = res.json()
            excepts = json.loads(excepts)
        elif point == 'VARIABLE':
            response = self.params[variable]
            excepts = str(excepts).strip()
        else:
            response = res.text

        if assertType == 'Contains':
            self.assertIn(str(excepts),str(response),msg='IN校验失败，实际返回值:{},期望值:{}'.format(response,excepts))
        else:
            self.assertEqual(response, excepts, msg='Equals校验失败，实际返回值:{},期望值:{}'.format(response, excepts))

    @staticmethod
    def getTestFunc(case,step,data):
        def func(self):
            self.action(case,step,data)
        return func

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

def generateCases():
    '''
    生成用例
    :return:
    '''
    #q = queue.deque()
    suites = unittest.TestSuite()
    cases = basePage.getCases()
    datas = basePage.getAllDatas()
    for data in datas:      #遍历数据sheet
        data_caseID = data[1]
        dataID = data[0]
        for case in cases:
            caseID = case[0]  #用例编号
            caseName = case[1]  #用例名称
            steps = basePage.getSteps(caseID)
            if data_caseID == caseID:       #对应用例id的数据
                case_name = 'test_{}_{}'.format(caseID,dataID)
                func = Cases.getTestFunc(case,steps,data)
                setattr(Cases,case_name,func)
                #q.append('test_{}'.format(caseID))
                suites.addTest(Cases(case_name))
    return suites


if __name__ == '__main__':

    suites = generateCases()
    fp = open("report\\result.html",'wb')
    runner = HTMLTestRunner3.HTMLTestRunner(
        stream=fp,
        title='Test Result',
        description='Test Case Run Result'
    )
    runner = unittest.TextTestRunner()
    runner.run(suites)
    fp.close()