from datetime import date, timedelta
import json
import sys
import tornado.web
import calendar
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1

class Testhandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('GET', 'OPTIONS', 'POST')

    user = MongoMixin.userDb[CONFIG['database'][0]['table'][12]['name']]
    company = MongoMixin.userDb[CONFIG['database'][0]['table'][13]['name']]
    branch = MongoMixin.userDb[CONFIG['database'][0]['table'][14]['name']]
    obBoard = MongoMixin.userDb[CONFIG['database'][0]['table'][16]['name']]
    payScale = MongoMixin.userDb[CONFIG['database'][0]['table'][17]['name']]
    attendance = MongoMixin.userDb[CONFIG['database'][0]['table'][18]['name']]
    holiday = MongoMixin.userDb[CONFIG['database'][0]['table'][20]['name']]
    leave = MongoMixin.userDb[CONFIG['database'][0]['table'][22]['name']]

    def options(self):
        code = 4100
        message = ''
        status = False
        result = []

    async def get(self):
        code = 4100
        message = ''
        status = False
        result = []

        try:
            token = self.request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                raise ValueError('Invalid - [ Authorization ]')

            payload = JWT_DECODE_1(token)
            if payload is None:
                raise ValueError('Invalid - [ Authorization ]')
            
            user_idQ = payload.get('_id')
            current_year = date.today().year
            current_month = date.today().month

            # print("**************",current_month)
    
            user_id = self.get_argument('user_id', ObjectId(user_idQ))
            year = int(self.get_argument('year', current_year))
            month = int(self.get_argument('month',current_month))

            first_day = date(year, month, 1)
            last_day_num = calendar.monthrange(year, month)[1]
            last_day = date(year, month, last_day_num)

            first_day_str = first_day.strftime('%Y-%m-%d')
            # print("*****************",first_day_str)
            last_day_str = last_day.strftime('%Y-%m-%d')
            # print("*****************",last_day_str)

            attendanceQ = self.attendance.aggregate([
                {
                    '$match': {
                        'user_id': ObjectId('6668259eb27f0e68666fa3ba'),
                        'date': {
                            '$gte': "2024-06-01",
                            '$lte': "2024-06-30"
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'date': 1,
                        'is_absent': 1,
                        'in_time': 1,
                        'out_time': 1
                    }
                }
            ])
            aaya=[]
            async for i in attendanceQ:
                aaya.append(i)
    
            # print("*****************",aaya)
            
            


            holidaysQ = self.holiday.aggregate([
                {
                    '$match': {
                        'date': {
                            '$gte': first_day_str,
                            '$lte': last_day_str 
                        }
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'date': 1
                    }
                }
            ])
            # print("*********",holidaysQ)
            chutti=[]
            async for i in holidaysQ:
                chutti.append(i)
            
            # print("88888888888888",chutti)


            leavesQ = self.leave.aggregate([
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'date': {
                            '$gte': first_day_str,
                            '$lte': last_day_str
                        },
                        'status': 'approved'
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'date': 1
                    }
                }
            ])

            attendance_records = {record['date']: record async for record in attendanceQ}
            # print("*&*&*&*&*&*&*&*&*&*&*&*&*&*&*",attendance_records)#{}
            holidays = {record['date']: record async for record in holidaysQ}
            # print("*&*&*&*&*&*&*&*&*&*&*&*&*&*&*",holidays)#{}
            approved_leaves = {record['date']: record async for record in leavesQ}
            # print("*&*&*&*&*&*&*&*&*&*&*&*&*&*&*",approved_leaves)#{}

            

            current_day = first_day
            while current_day <= last_day:
                day_str = current_day.strftime('%Y-%m-%d')
                if day_str in attendance_records:
                    result.append(attendance_records[day_str])
                elif day_str in holidays:
                    result.append({
                        'date': day_str,
                        'is_absent': False,
                        'holiday': True,
                        'in_time': None,
                        'out_time': None
                    })
                elif day_str in approved_leaves:
                    result.append({
                        'date': day_str,
                        'is_absent': False,
                        'holiday': False,
                        'leave': True,
                        'in_time': None,
                        'out_time': None
                    })
                elif current_day.weekday() >= 5:  # Saturday and Sunday
                    result.append({
                        'date': day_str,
                        'is_absent': False,
                        'holiday': True,
                        'in_time': None,
                        'out_time': None
                    })
                else:
                    result.append({
                        'date': day_str,
                        'is_absent': True,
                        'holiday': False,
                        'leave': False,
                        'in_time': None,
                        'out_time': None
                    })
                current_day += timedelta(days=1)

            result = sorted(result, key=lambda x: x['date'])
            status = True
            code = 2000
            message = 'Data fetched successfully'

        except ValueError as ve:
            code = 4001
            message = str(ve)
            Log.i(message)
        except Exception as e:
            template = 'Exception: {0}. Argument: {1!r}'
            iMessage = template.format(type(e).__name__, e.args)
            message = 'Internal Error, Please Contact the Support Team.'
            Log.w('EXC', iMessage)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.d('EX2', f'FILE: {fname} LINE: {exc_tb.tb_lineno} TYPE: {exc_type}')

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }


        try:
            self.write(json.loads(bdumps(response)))
            await self.finish()
        except Exception as e:
            code = 5011
            message = 'Internal Error, Please Contact the Support Team.'
            iMessage = f'Exception: {type(e).__name__}. Argument: {e.args!r}'
            Log.w('EXC', iMessage)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.d('EX2', f'FILE: {fname} LINE: {exc_tb.tb_lineno} TYPE: {exc_type}')
            response = {
                'code': code,
                'status': False,
                'message': message
            }
            self.write(json.loads(bdumps(response)))
            await self.finish()
