from datetime import datetime

import pandas as pd
from django.http import HttpResponse
from product.models import PCB


def addTestData(request):
    if request.method == 'GET':
        cnt = 0
        date_format = "%Y-%m-%d %H:%M:%S"
        df = pd.read_csv('../cache/PCB.csv')
        for index, row in df.iterrows():
            pcb = PCB(record_time=datetime.strptime(row['record_time'], date_format), line_no=row['line_no'],
                      picture_file_name=row['pic_file_name'], has_defect=row['has_defect'], mh=row['mh'],
                      mb=row['mb'], oc=row['oc'], sh=row['sh'], sp=row['sp'], spc=row['spc'])
            pcb.save()
            cnt += 1
        # 顺便新增用户数据，暂时弃用
        # user1 = User(user_name='user1', email='u1@mail.com',
        #                     passwd='gg', full_name="张三", role='admin' )
        # user1.save()
        # user2 = User(user_name='user2', email='u2@mail.com',
        #                     passwd='gg', full_name="李四")
        # user2.save()
        # user3 = User(user_name='user3', email='u3@mail.com',
        #                     passwd='gg', full_name="王五")
        # user3.save()
    return HttpResponse("PCB data should be loaded"
                        # + "3 users added\n"+str(user1)+'\n'+str(user2)+'\n'+str(user3)+'\n'
                        , status=200)
