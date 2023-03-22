# -*- coding: utf-8 -*-
import datetime
import operator

import pandas as pd
import pymysql
import requests

import json
from readConfig import ReadConfig


def main():
    filename = f'客户信息_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.xlsx'
    page = int(config.get_ini("GETDATA", "page"))
    limit = int(config.get_ini("GETDATA", "total"))

    get_search_lists(filename, page, limit)


def get_search_lists(filename: str, page_num: int, limit: int):
    api = config.get_ini("API", "api_url")
    url = f"{api}/clue/listNewV3"

    params = {
        "pageNum": 1, "pageSize": 10, "orderBy": [{"field": "putPoolTime", "orderByType": "DESC"}],
        "myDiClue": False, "myFollowClue": False, "optStatus": "ORG_TO_DISTRIBUTE", "newSelect": "N_ALL"
    }

    handledCnt = 0
    successCnt = 0

    for page in range(page_num):
        pageNum = page + 1
        pageSize = params['pageSize']

        print(f"[+] 正在爬取##################################第 {pageNum} 页#####################################")
        params['pageNum'] = pageNum
        response = requests.get(url, params=params, headers=headers)
        # print(response.text)
        rsp_json = json.loads(response.content)

        data_list = rsp_json['data']['list']
        print('第', pageNum, '页获取记录数：', len(data_list))

        for i in range(len(data_list)):
            recordNum = (pageSize * page) + (i + 1)
            item = data_list[i]
            if handledCnt < limit:
                print(f"[+] 开始处理第{i}条...")
                saveFlag = get_customer_detail(filename, recordNum, item['clueId'])
                handledCnt += 1
                if saveFlag:
                    successCnt += 1
                # sleep(5)
                print(f"[+] 第{i}条处理完毕...\n")
            else:
                # 跳出处理循环
                break

        # 跳出分页循环
        if handledCnt >= limit:
            break

        print("已处理总数：", handledCnt, "入库总数：", successCnt)


def get_customer_detail(filename: str, idx: int, clueId: str):
    api = config.get_ini("API", "api_url")
    url = f"{api}/work/panel/copyUser/list?clueId={clueId}"
    response = requests.get(url, headers=headers)
    # print(response.text)
    rsp_json = json.loads(response.content)
    detail_info = rsp_json['data']
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '获取用户信息：', detail_info)

    info = {
        '用户id': [],
        '姓名': [],
        '手机号码': [],
        '城市': [],
        '金额': [],
        '营业执照/纳税': [],
        '公积金': [],
        '车': [],
        '房': [],
        '资质扩展信息': [],
        '寿险保单': [],
        '银行代发': [],
        '推送状态(新客户填4)': [],
        '贷款类型': [],
        '修改人': [],
        '职业': [],
        '年龄': [],
        '性别(1-男, 2-女)': [],
        '渠道': [],
        '手机归属地': [],
        'IP归属地': [],
        '是否异地': [],
        '类型': [],
        '生成sql': [],
    }

    info['用户id'].append(idx)
    info['姓名'].append(detail_info['customer']['name'])
    info['手机号码'].append(detail_info['customer']['mobile'])

    location = detail_info['customer']['location']
    city = str(location).split("-")[1] + '市'
    info['城市'].append(city)

    loanIntentionLoanAmount = int(detail_info['loanIntention']['loanAmount'])
    if loanIntentionLoanAmount >= 200000:
        loanAmount = '20万'
    elif loanIntentionLoanAmount >= 100000 and loanIntentionLoanAmount < 200000:
        loanAmount = '10-20万'
    else:
        loanAmount = '5-10万'

    info['金额'].append(loanAmount)

    remark = detail_info['customer']['remark']
    hasSalary = 0
    hasPublicFund = 0
    hasBusinessLicense = 0
    hasHouse = 0
    hasCar = 0
    hasInsurance = 0

    if operator.contains(remark, '有代发工资'):
        hasSalary = 1
    if operator.contains(remark, '有公积金'):
        hasPublicFund = 1
    if operator.contains(remark, '有营业执照'):
        hasBusinessLicense = 1
    if operator.contains(remark, '有商品房'):
        hasHouse = 1
    if operator.contains(remark, '有私家车'):
        hasCar = 1
    if operator.contains(remark, '有人寿保险'):
        hasInsurance = 1

    info['营业执照/纳税'].append(hasBusinessLicense)
    info['公积金'].append(hasPublicFund)
    info['车'].append(hasCar)
    info['房'].append(hasHouse)
    info['资质扩展信息'].append('')
    info['寿险保单'].append(hasInsurance)
    info['银行代发'].append(hasSalary)
    info['推送状态(新客户填4)'].append(4)
    info['贷款类型'].append('web')
    info['修改人'].append(0)
    info['职业'].append(1)
    info['年龄'].append(detail_info['customer']['age'])

    gender = 0
    sex = detail_info['customer']['sex']
    if sex == "男":
        gender = 1
    elif sex == '女':
        gender = 2
    info['性别(1-男, 2-女)'].append(gender)

    info['渠道'].append('zxf-ttt-001')
    info['手机归属地'].append('')
    info['IP归属地'].append('')
    info['是否异地'].append(0)
    info['类型'].append(0)

    USER_ID = idx + 1
    NAME = info.get('姓名')[0]
    MOBILE = info.get('手机号码')[0]
    CITY = info.get('城市')[0]
    LOAN_AMOUNT = info.get('金额')[0]
    CREDIT_CARD = '0'
    PUBLIC_FUND = hasPublicFund
    CAR = hasCar
    HOUSE = hasHouse
    HOUSE_EXTENSION = 0
    INSURANCE = hasInsurance
    GETWAY_INCOME = hasSalary
    LEVEL = '1'
    CREATE_BY = '4'
    AGE = info.get('年龄')[0]
    GENDER = info.get('性别(1-男, 2-女)')[0]
    CHANNEL = info.get('渠道')[0]
    MOBILE_LOCATION = info.get('手机归属地')[0]
    IP_LOCATION = info.get('IP归属地')[0]
    IN_CITY = info.get('是否异地')[0]
    MD5 = '0'
    TYPE = info.get('类型')[0]
    EXTENSION = ''

    info['生成sql'].append(
        f"""INSERT INTO `user_aptitude`(`USER_ID`,`NAME`,`MOBILE`,`CITY`,`LOAN_AMOUNT`,`CREDIT_CARD`,`PUBLIC_FUND`,`CAR`,`HOUSE`,`HOUSE_EXTENSION`,`INSURANCE`,`GETWAY_INCOME`,`LEVEL`,`CREATE_BY`,`AGE`,`GENDER`,`CHANNEL`,`MOBILE_LOCATION`,`IP_LOCATION`,`IN_CITY`,`MD5`,`TYPE`,`EXTENSION`) VALUES ('{USER_ID}','{NAME}','{MOBILE}','{CITY}','{LOAN_AMOUNT}','{CREDIT_CARD}','{PUBLIC_FUND}','{CAR}','{HOUSE}','{HOUSE_EXTENSION}','{INSURANCE}','{GETWAY_INCOME}','{LEVEL}','{CREATE_BY}','{AGE}','{GENDER}','{CHANNEL}','{MOBILE_LOCATION}','{IP_LOCATION}','{IN_CITY}','{MD5}','{TYPE}','{EXTENSION}');""")

    return save_data2excel(filename, pd.DataFrame(info))


def save_data2excel(name: str, new_data: dict):
    try:
        data = pd.read_excel(name)
    except:
        data = pd.DataFrame({
            '用户id': [],
            '姓名': [],
            '手机号码': [],
            '城市': [],
            '金额': [],
            '营业执照/纳税': [],
            '公积金': [],
            '车': [],
            '房': [],
            '资质扩展信息': [],
            '寿险保单': [],
            '银行代发': [],
            '推送状态(新客户填4)': [],
            '贷款类型': [],
            '修改人': [],
            '职业': [],
            '年龄': [],
            '性别(1-男, 2-女)': [],
            '渠道': [],
            '手机归属地': [],
            'IP归属地': [],
            '是否异地': [],
            '类型': [],
            '生成sql': [],
        })

    # 存储到Excel
    save = pd.concat([data, new_data], axis=0)
    save.to_excel(name, index=False)

    # 存储到数据库
    store_database_sw = config.get_ini("GETSW", "store_database")
    if store_database_sw == 'true':
        if not is_db_existed(new_data):
            insertSql = new_data['生成sql'][0]
            insertCnt = save_data2db(insertSql)
            return insertCnt > 0
        else:
            NAME = new_data['姓名'][0]
            MOBILE = new_data['手机号码'][0]
            print("已在库忽略用户信息", NAME, MOBILE)
            return False


def is_db_existed(new_data: dict):
    cursor = db.cursor()

    # SQL 查询语句
    NAME = new_data['姓名'][0]
    MOBILE = new_data['手机号码'][0]
    sql = f"SELECT * FROM `user_aptitude` WHERE NAME = '{NAME}' AND MOBILE = '{MOBILE}'"

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        print(NAME, MOBILE, "在库信息：", results)
        cursor.close()
        return len(results) > 0
    except:
        return False


def save_data2db(insertSql: str):
    cursor = db.cursor()
    try:
        # 这个是执行sql语句，返回的是影响的条数
        print(insertSql)
        data = cursor.execute(insertSql)
        db.commit()
        cursor.close()
        return data
    except pymysql.Error as e:
        print(e)
        print('操作数据库失败')
        return 0


def get_access_token():
    return 'token'


if __name__ == '__main__':
    config = ReadConfig()  # 实例化

    get_authorization = get_access_token()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/54.0.2840.99 Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        'Authorization': 'Bearer {}'.format(get_authorization)
    }

    db = pymysql.connect(host=config.get_ini("DATABASE", "host"),
                         port=int(config.get_ini("DATABASE", "port")),
                         user=config.get_ini("DATABASE", "username"),
                         password=config.get_ini("DATABASE", "password"),
                         db=config.get_ini("DATABASE", "database"), charset='utf8')

    main()

    db.close()
    print("[+] Spider success end ...")
