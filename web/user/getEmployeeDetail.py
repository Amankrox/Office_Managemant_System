import calendar
import json
import sys
from datetime import datetime, timedelta, timezone

import tornado.web
from bson import ObjectId
from build_config import CONFIG
from util.conn_util import MongoMixin
from util.log_util import Log
from util.time_util import timeNow
from bson.json_util import dumps as bdumps
from helper.jwt_helper import JWT_DECODE_1, JWT_ENCODE_1
from helper.decorators import all_origin

class getEmployeeDetailHandler(tornado.web.RequestHandler, MongoMixin):
    SUPPORTED_METHODS = ('OPTIONS', 'GET')

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
    project = MongoMixin.userDb[
        CONFIG['database'][0]['table'][19]['name']
    ]
    account = MongoMixin.userDb[
        CONFIG['database'][0]['table'][21]['name']
    ]
    paySlip = MongoMixin.userDb[
        CONFIG['database'][0]['table'][23]['name']
    ]
    project = MongoMixin.userDb[
        CONFIG['database'][0]['table'][19]['name']
    ]
    assignProject=MongoMixin.userDb[
        CONFIG['database'][0]['table'][25]['name']
    ]
    calander=MongoMixin.userDb[
        CONFIG['database'][0]['table'][26]['name']
    ]
    role=MongoMixin.userDb[
        CONFIG['database'][0]['table'][15]['name']
    ]
    leave=MongoMixin.userDb[
        CONFIG['database'][0]['table'][22]['name']
    ]

    def options(self):
        self.set_status(204)
        self.finish()

    async def get(self):
        code = 4100
        message = ''
        status = False
        result = []

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

            user_id = payload.get('userId')
            role = payload.get('userRole')
            company_id = payload.get('companyId')

            
            


            # print("****",comp_name)
            if role not in ['branchManager', 'HR-1', 'HR-2', 'HR-3']:
                code=4003
                message='You are not Authorized to use this'
                status=False
                raise Exception
            # converting the body into json
            # print('**********')
            try:
                self.request.arguments=json.loads(self.request.body)

            except Exception as e:
                code=4004      
                message='Expected request type json'
                status=False
                raise Exception

            empUserId=self.request.arguments.get('empUserId')
            # print("userID",empUserId)
            if not empUserId:
                    message = 'employyee id is not coorect.'
                    code = 7003
                    status = False
                    raise Exception
                
            sartDate1=self.request.arguments.get('sartDate1')
            # print("*****************",sartDate1)
            if not sartDate1:
                    message = 'startDate1  is not coorect.'
                    code = 7004
                    status = False
                    raise Exception
                
            endDate1=self.request.arguments.get('endDate1')
            # print("*****************",endDate1)
            if not endDate1:
                    
                    message = 'EndDate1 id is not coorect.'
                    code = 7005
                    status = False
                    raise Exception
            sartDate2=self.request.arguments.get('sartDate2')
            # print("*****************",sartDate2)
            if not sartDate2:
                    message = 'startDate2 is not coorect.'
                    code = 7004
                    status = False
                    raise Exception
                
            endDate2=self.request.arguments.get('endDate2')
            # print("*****************",endDate2)
            if not endDate2:
                    
                    message = 'EndDate2 id is not coorect.'
                    code = 7005
                    status = False
                    raise Exception


            

            company_role_NameQ=self.user.aggregate(
                 [
                    {
                        '$match': {
                            '_id': ObjectId(empUserId)
                        }
                    }, {
                        '$lookup': {
                            'from': 'role', 
                            'localField': 'role', 
                            'foreignField': '_id', 
                            'as': 'userRole'
                        }
                    }, {
                        '$lookup': {
                            'from': 'company', 
                            'localField': 'companyId', 
                            'foreignField': '_id', 
                            'as': 'userCompany'
                        }
                    }, {
                        '$project': {
                            '_id': 0, 
                            'email':1,
                            'companyId':1,
                            'branchId':1,
                            'role':1,
                            'createdBy':1,
                            'PersonalInfo':1,
                            'companyName': {
                                '$arrayElemAt': [
                                    '$userCompany.companyName', 0
                                ]
                            }, 
                            'roleName': {
                                '$arrayElemAt': [
                                    '$userRole.role', 0
                                ]
                            }
                            
                        }
                    }
                ]
            )
            # print("*********",company_role_NameQ)
            if not company_role_NameQ:
                 code=40004
                 message="cannot able to find company name and role  "
                 status=False
                 raise Exception
            company_role_Name=[]
            async for i in company_role_NameQ:
                company_role_Name.append(i)
            # print("*********",company_role_Name)
            personal_info = company_role_Name[0]['PersonalInfo']
            # print("*******",personal_info)
            full_name = f"{personal_info['firstName']} {personal_info['lastName']}"
            phone = personal_info['phone']
            createdBy=company_role_Name[0]['createdBy']
            # int("pr55555555555555555565555",createdBy)
            createdByNameQ= self.user.aggregate(
                 [
                    {
                        '$match': {
                            '_id': ObjectId(createdBy)
                        }
                    }, {
                        '$project': {
                            'PersonalInfo.firstName': 1, 
                            'PersonalInfo.lastName': 1, 
                            'PersonalInfo.phone':1,
                            '_id': 0
                        }
                    }
                ]
            )
            if not createdByNameQ:
                 code=40009
                 message="cannot able to find name   "
                 status=False
                 raise Exception
            createdByName=[]
            async for i in createdByNameQ:
                createdByName.append(i)
            # print("55555555555555555565555",createdByNameQ)
            # print("55555555555555555565555",createdByName[0]['PersonalInfo'])
            creatorName=createdByName[0]['PersonalInfo']
            # print("55555555555555555565555",creatorName)
            creatorname1=f"{creatorName['firstName']} {creatorName['lastName']}"
            creatorPhone=creatorName['phone']
            
            

            startDate1 = sartDate1
            endDate1 = endDate1
            month1 = datetime.strptime(startDate1, '%Y-%m-%d').month
    
            month_name1 = datetime.strptime(startDate1, '%Y-%m-%d').strftime('%B')
            month_days1=calendar.monthrange(datetime.strptime(startDate1, '%Y-%m-%d').year, datetime.strptime(startDate1, '%Y-%m-%d').month)[1]
            # print('***month name***********',month_days1)
            month2 = datetime.strptime(sartDate2, '%Y-%m-%d').month
            # print('month is *************',month2)
            month_name2 = datetime.strptime(sartDate2, '%Y-%m-%d').strftime('%B')
            month_days2=calendar.monthrange(datetime.strptime(sartDate2, '%Y-%m-%d').year, datetime.strptime(sartDate2, '%Y-%m-%d').month)[1]
            year=2024
            num_saturdays = sum(1 for day in range(1,  month_days1 + 1) if calendar.weekday(year, month1 , day) == calendar.SATURDAY)
            num_sundays = sum(1 for day in range(1,  month_days1 + 1) if calendar.weekday(year, month1 , day) == calendar.SUNDAY)
            sum_sat_sun=num_saturdays+num_sundays

            num_saturdays2 = sum(1 for day in range(1,  month_days2 + 1) if calendar.weekday(year, month2 , day) == calendar.SATURDAY)
            num_sundays2 = sum(1 for day in range(1,  month_days2 + 1) if calendar.weekday(year, month2 , day) == calendar.SUNDAY)
            sum_sat_sun2=num_saturdays2+num_sundays2
    
    
            # print('***month name***********',num_saturdays)
            # print('***month name***********',num_sundays)
            if not startDate1:
                code = 4333
                message = 'Please enter the valid date in the format of YYYY-MM-DD.'
                status = False
                raise Exception

            startdate1 = str(startDate1)
            enddate1 = str(endDate1)

            startdate2 = str(sartDate2)
            enddate2 = str(endDate2)
            # print("*****************",endDate2)

            presentDayQ = self.attendance.aggregate(
                [
                    {
                        '$match': {
                            'user_id': ObjectId(empUserId), 
                            'is_absent': False, 
                            'date': {
                                '$gte': startdate1, 
                                '$lte': enddate1
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
            # print("******************",presentDayQ)
            presentDay = []
            async for i in presentDayQ:
                presentDay.append(i)
            # print("******************",presentDay)
            if not presentDay:
                attendance = ["The user has not attended this month"]
            else:
                lateCount = presentDay[0]['is_late_count']
                leaveCount = presentDay[0]['leave_count']
                totalPresentDay = presentDay[0]['total_present_days']
                attendance = [
                    f"total working day:{(month_days2-sum_sat_sun2)}",
                    f"total Absent :{( month_days1 - totalPresentDay-sum_sat_sun)}",
                    f"Late count: {lateCount}",
                    f"Leave count: {leaveCount}",
                    f"Total present days: {totalPresentDay}"
                ]
            # print("******************",lateCount,leaveCount,totalPresentDay)
            try:
                totalLeaveQ=self.leave.aggregate(
                     
                    [
                        {
                            '$addFields': {
                                'leaveDate': {
                                    '$toDate': '$leaveDate'
                                }
                            }
                        }, {
                            '$match': {
                                'userId': ObjectId(empUserId), 
                                'isApproved': True, 
                                'leaveDate': {
                                    '$lte': datetime(2024, 6, 30, 0, 0, 0, tzinfo=timezone.utc), 
                                    '$gte': datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
                                }
                            }
                        }, {
                            '$count': 'approvedLeaves'
                        }
                    ]
                 )
                # print("*****************",totalLeaveQ)
                totalLeave = []
                async for i in totalLeaveQ:
                    totalLeave.append(i)
                # print("*****************",totalLeave)

                if not totalLeave:
                    totalLeaveQ21 = ["The user has not taken any leave yet"]
                else:
                    totalLeaveQ2 = totalLeave[0]['approvedLeaves']
                    totalLeaveQ21 = [f"Total approved leaves: {totalLeaveQ2}"]
                # print("******************",totalLeaveQ2)
            except Exception as e:
                code=4366
                message='probelm in line no 342'
                status=False
                raise Exception    

            try:

                presentDayQ2 = self.attendance.aggregate(
                    
                    [
                        {
                            '$match': {
                                'user_id': ObjectId(empUserId), 
                                'is_absent': False, 
                                'date': {
                                    '$gte': startdate2, 
                                    '$lte': enddate2
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
                # print("*********************",presentDayQ2)
                presentDay2 = []
                async for i in presentDayQ2:
                    presentDay2.append(i)

                if not presentDay2:
                    attendance2 = ["The user has not attended this month"]
                else:
                    lateCount1 = presentDay2[0]['is_late_count']
                    leaveCount1 = presentDay2[0]['leave_count']
                    totalPresentDay1 = presentDay2[0]['total_present_days']
                    attendance2 = [
                        f"total working day:{(month_days2-sum_sat_sun)}",
                        f"total Absent :{( month_days1 - totalPresentDay1-sum_sat_sun2)}",
                        f"Late count: {lateCount1}",
                        f"Leave count: {leaveCount1}",
                        f"Total present days: {totalPresentDay1}"
                    ]
                # print("******************",lateCount2,totalLeaveQ2,totalPresentDay2)
            
            except Exception as e:
                code=400
                message='probelm in line no279'
                status=False
                raise Exception
            


            salaryQ = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(empUserId),
                            'month':month2
                        }
                    }, {
                        '$project': {
                            'baseSalary': 1, 
                            'finalSalary': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            salary = []
            async for i in salaryQ:
                salary.append(i)
            if not salary:
                monthsSalary1 = [
                    "Salary is not generated for this month"
                ]
            else:
                baseSalary = salary[0]['baseSalary']
                finalSalary = round(salary[0]['finalSalary'])
                monthsSalary1 = [
                    f"Base Salary: {baseSalary}",
                    f"Final Salary: {finalSalary}"
                ]
                
            
            salaryQ2 = self.paySlip.aggregate(
                [
                    {
                        '$match': {
                            'userId': ObjectId(empUserId),
                            'month':month1
                        }
                    }, {
                        '$project': {
                            'baseSalary': 1, 
                            'finalSalary': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            salary2 = []
            async for i in salaryQ2:
                salary.append(i)
            if not salary2:
                monthsSalary2 = [
                    "Salary is not generated for this month"
                ]
            else:
            
                baseSalary2 = salary2[0]['baseSalary']
                finalSalary2 = round(salary2[0]['finalSalary'])
                monthsSalary2 = [
                    f"Base Salary: {baseSalary2}",
                    f"Final Salary: {finalSalary2}"
                ]

            projectQ = self.assignProject.aggregate(
                [
                    {
                        '$match': {
                            'users': {
                                '$in': [
                                    ObjectId(empUserId)
                                ]
                            }
                        }
                    }, {
                        '$project': {
                            'project_id': {'$toString':'$project_id'
                            }, 
                            'AssignedOn': 1, 
                            'tasks.taskId': 1, 
                            'tasks.taskName': 1, 
                            'tasks.dueDate': 1, 
                            '_id': 0
                        }
                    }
                ]
            )
            projects = []
            async for i in projectQ:
                projects.append(i)
            if not projects:
                 projectDetails=["the user is not assigned with any projects the user is still on bench"]
            else:
                projectDetails = [
                    {
                        "Project": f"{index + 1}",
                        "project_id": project['project_id'],
                        "Date_of_Assign": project['AssignedOn'],
                        "List_of_tasks": [
                            {
                                "taskId": task['taskId'],
                                "taskName": task['taskName'],
                                "dueDate": task['dueDate']
                            }
                            for task in project['tasks']
                        ]
                    }
                    for index, project in enumerate(projects)
                ]

            # print('**********************',datetime.now().date())
            

            response_data = {
                "Result": [
                    {
                        "Employee_info": {
                            # "companyId": str(company_role_Name[0]['companyId']),
                            "comp_name":company_role_Name[0]['companyName'],
                            # "branchId": str(company_role_Name[0]['branchId']),
                            # "user_id": str(empUserId),
                            "name": full_name,
                            "mobile_no.":phone,
                            "email": company_role_Name[0]['email'],
                            # "role_id": str(company_role_Name[0]['role']),
                            "role_name":company_role_Name[0]['roleName'],
                            "createdBy": creatorname1,
                            "Cteator_phone":creatorPhone
                        },
                        "Month": {
                            month_name1: {
                                "attendance":attendance,
                                "salary":monthsSalary2
                                # "message":message1,
                                # "total_working_days": month_days1-sum_sat_sun,
                                # "total_present": totalPresentDay,
                                # "total_absent": month_days1 - totalPresentDay-sum_sat_sun,
                                # "Leave_taken": leaveCount,
                                # "late_Count":lateCount,
                                #  "base_Salary":baseSalary,
                                # "salary_taken": finalSalary2
                                
                            },
                            month_name2: {
                                "attendance":attendance2,
                                "salary":monthsSalary1
                                # "message":message2,
                                # "total_working_days":month_days2-sum_sat_sun2,
                                # "total_present": totalPresentDay2,
                                # "total_absent": month_days2 - totalPresentDay2-sum_sat_sun2,
                                # "Leave_taken": totalLeaveQ2,
                                # "late_Count":lateCount2,
                                # "base_Salary":baseSalary,
                                # "salary_taken": finalSalary
                            }
                        },
                        "Task": projectDetails
                    }
                ]
            }
            code = 200
            message = 'Data fetched successfully'
            result = response_data
            status = True

        except Exception as e:
            status = False
            if not message:
                template = 'Exception: {0}. Argument: {1!r}'
                code = 5010
                iMessage = template.format(type(e).__name__, e.args)
                message = 'Internal Error, Please Contact the Support Team.'
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
            message = 'Internal Error, Please Contact the Support Team.'
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
                pass
