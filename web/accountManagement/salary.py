import calendar
import json
import sys
from datetime import datetime, timedelta

from pymongo import UpdateOne
import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin
class getPaySlipHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET', 'POST')

    user = MongoMixin.userDb[
        CONFIG['database'][0]['table'][12]['name']
    ]

    company = MongoMixin.userDb[
        CONFIG['database'][0]['table'][13]['name']
    ]

    branch = MongoMixin.userDb[
        CONFIG['database'][0]['table'][14]['name']
    ]

    obBoard = MongoMixin.userDb[
        CONFIG['database'][0]['table'][16]['name']
    ]
    payScale = MongoMixin.userDb[
        CONFIG['database'][0]['table'][17]['name']
    ]

    attendance = MongoMixin.userDb[
        CONFIG['database'][0]['table'][18]['name']
    ]
    account= MongoMixin.userDb[
        CONFIG['database'][0]['table'][21]['name']
    ]
    paySlip = MongoMixin.userDb[
        CONFIG['database'][0]['table'][23]['name']
    ]



    def options(self):
        status = False
        code = 4100
        message = ''
        result = []

    async def post(self):
        code = 4100
        message = ''
        status = False
        result = []

        try:
            try:
                # get the token from header
                token = self.request.headers.get('Authorization')
                if token:
                    token = token.replace('Bearer ', '')
                else:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception

                # decode the token
                payload = JWT_DECODE_1(token)
                if payload is None:
                    code = 4001
                    message = 'Invalid - [ Authorization ]'
                    status = False
                    raise Exception
            except Exception as e:
                Log.i(e)
                code = 4001
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            user_id = payload.get('userId')
            # print('*****************************',user_id)
            role = payload.get('userRole')
            company_id=payload.get('companyId')
            # print('*****************************',role)
            if role != 'AccountsManager':
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception

            userQ = self.user.find({'_id': ObjectId(user_id)})

            user = []
            async for i in userQ:
                user.append(i)
            if user is None:
                code = 4001
                message = 'Invalid - [ Authorization ]'
                status = False
                raise Exception

            try:
                # decode json
                self.request.arguments = json.loads(self.request.body)

            except Exception as e:
                code = 4100
                status = False
                message = 'Expected Request Type JSON.'
                raise Exception
            

            try:
                empUserId=self.request.arguments.get('empUserId')
                # print("**********userId********8",empUserId)
            except Exception as e:
                code = 404
                status = False
                message= 'plz enter the valid empUser'

            

            startDate=self.request.arguments.get('startDate')
            startDate = datetime.strptime(startDate, '%Y-%m-%d').date()

            if startDate is None or not startDate:
                code = 4333
                message ='plz enter the valid date in the format of YYYY-MM-DD.',
                status = False
                raise Exception
            
            # print('*************',startDate)


            endDate=self.request.arguments.get('endDate')
            endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
            currentYear = endDate.year
            mmonths = endDate.month
            num_days_in_month = calendar.monthrange(currentYear, mmonths)[1]

            print("**********************", mmonths)


            if endDate is None or not endDate:
                code = 4333
                message ='plz enter the valid date in the format of YYYY-MM-DD.',
                status = False
                raise Exception
            
            # print('*************',endDate)           
            
            try:
                accountQ=self.account.aggregate(
                    [
                        {
                            '$match': {
                                'userId': ObjectId(empUserId)   
                            }
                        },
                          {
                            '$project': {
                                'companyId': 1, 
                                'branchId': 1, 
                                'payGrade': 1,
                                'baseSalary':1,
                                'performanceBounous': 1, 
                                'singingBonous': 1, 
                                '_id': 0
                            }
                        }
                    ]
                )

                account = []

                async for i in accountQ:
                    account.append(i)
                    account[0]['companyId'] = str(account[0]['companyId'])
                    account[0]['branchId'] = str(account[0]['branchId'])
                if not account:
                    
                    
                    baseSalary=0
                    branch_id=0
                    payGrade=0
                    performanceBonous=0
                    singingBounous=0
                else:
                    baseSalary=account[0]['baseSalary']
                    branch_id=account[0]['branchId']
                    payGrade=account[0]['payGrade']
                    performanceBonous=account[0]['performanceBounous']
                    singingBounous=account[0]['singingBonous']

                # print(account[0]['baseSalary'])

                result = account

            except Exception as e:
                code=400
                message='noting getting the value in line 170'
                status=False
                raise Exception
            
            try:
                startDate = str(startDate)
                endDate = str(endDate)
                print(startDate)
                print(endDate)
                presentDayQ= self.attendance.aggregate(
                    [
                        
                        {
                            '$match': {
                                'user_id': ObjectId(empUserId), 
                                'is_absent': False, 
                                'date': {
                                    '$gte': startDate, 
                                    '$lte': endDate
                                }
                            }
                        }, {
                            '$group': {
                                '_id': None, 
                                'is_late_count': {
                                    '$sum': {
                                        '$cond': [
                                            '$is_late', 1, 0
                                        ]
                                    }
                                }, 
                                'leave_count': {
                                    '$sum': {
                                        '$cond': [
                                            '$leave', 1, 0
                                        ]
                                    }
                                }, 
                                'total_present_days': {
                                    '$sum': 1
                                }
                            }
                        }, {
                            '$project': {
                                '_id': 0, 
                                'is_late_count': 1, 
                                'leave_count': 1, 
                                'total_present_days': 1
                            }
                        }
                    ]
                )
                presentDay=[]
                async for i in presentDayQ:
                    presentDay.append(i)
                #     print('***************',presentDay[0]['total_present_days'])
                # print('*************',presentDay)
                if not presentDay:
                 

                    lateCount=0
                # print("**********",lateCount)
                    leaveCount=0
                    totalPresentDay=0
                # print("**********",totalPresentDay,leaveCount,lateCount)
                else:
                    lateCount=presentDay[0]['is_late_count']
                # print("**********",lateCount)
                    leaveCount=presentDay[0]['leave_count']
                    totalPresentDay=presentDay[0]['total_present_days']

            except Exception as e:
                code=402
                message='check your presentDay  aggeregate part'
                status= False
                raise Exception
            num_saturdays = sum(1 for day in range(1,  num_days_in_month + 1) if calendar.weekday(currentYear, mmonths , day) == calendar.SATURDAY)
            num_sundays = sum(1 for day in range(1,  num_days_in_month + 1) if calendar.weekday(currentYear, mmonths, day) == calendar.SUNDAY)
            sum_sat_sun=num_saturdays+num_sundays
            dailySalary = baseSalary / (num_days_in_month- sum_sat_sun) 
            totalPresent = totalPresentDay  - leaveCount
            finalSalary= ((dailySalary * totalPresent)+ performanceBonous)
            # print("**********",finalSalary)



            payslip_existsQ = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(empUserId)
                        }
                    }
                ]
            )
            # print("************",payslip_existsQ)
            payslip_exists=[]

            async for i in payslip_existsQ:
                payslip_exists.append(i) 
            

            # Add singing bonus only if no payslip exists
            if not payslip_exists:
                finalSalary += singingBounous
            else:
                bulk_operations = [
                        UpdateOne(
                            {'_id': payslip['_id']},
                            {'$set': {'isActive': False}}
                        ) for payslip in payslip_exists
                    ]

                # Execute bulk write operations
                resulttt = await self.paySlip.bulk_write(bulk_operations)
                if resulttt:
                    code=200
                    message="updated and added successfully"
                    status=True
            # If late more than 3 days, deduct one day's salary
            if lateCount > 3:
                finalSalary -= dailySalary
            # print("***************")
            data={
                'companyId':ObjectId(company_id),
                'branchId':ObjectId(branch_id),
                'userId':ObjectId(empUserId),
                'createdBy':ObjectId(user_id),
                'payGrade':payGrade,
                'baseSalary':baseSalary,
                'finalSalary':finalSalary,
                'month':mmonths,
                'performanceBounous':performanceBonous,
                'singingBonous':singingBounous,
                'createdAt':datetime.now(),
                'isActive':True
            }
            try:
                await self.paySlip.insert_one(data)
                code = 200
                status = True
                message = 'salary added succesfully'
                result=result

            except Exception as e:
                code = 43315
                status =False
                message = 'faild to add salary'
                raise Exception


        except Exception as e:
            status = False
            if not len(message):
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'this user did not started their office yet,no data found, Please Contact the Support Team.'
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = exc_tb.tb_frame.f_code.co_filename
                Log.w('EXC', iMessage)
                Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }
        Log.d('RSP', response)
        try:
            self.write(json.loads(bdumps(response)))
            await self.finish()
            return
        except Exception as e:
            status = False
            template = 'Exception: {0}. Argument: {1!r}'
            code = 5011
            iMessage = template.format(type(e).__name__, e.args)
            message = ' Please Contact the Support Team.'
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = exc_tb.tb_frame.f_code.co_filename
            Log.w('EXC', iMessage)
            Log.d('EX2', 'FILE: ' + str(fname) + ' LINE: ' + str(exc_tb.tb_lineno) + ' TYPE: ' + str(exc_type))
            response = {
                'code': code,
                'status': status,
                'message': message
            }
            self.write(json.loads(bdumps(response)))
            await self.finish()
            