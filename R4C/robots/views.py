import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Robot
import json
import pytz
from datetime import datetime, timedelta


@csrf_exempt
def create_robot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model = data.get('model')
            version = data.get('version')
            dt_obj = datetime.strptime(
                data.get('created'), '%Y-%m-%d %H:%M:%S'
            )

            created = pytz.timezone('UTC').localize(dt_obj)

            if not Robot.objects.filter(model=model, version=version,
                                        created=created).exists():
                robot = Robot(model=model, version=version, created=created)
                robot.save()
                return JsonResponse(
                    data={'message': 'Робот успешно создан'}, status=200
                )
            return JsonResponse(
                data={'message': 'Такой робот уже есть в базе данных'},
                status=200
            )

        except Exception as e:
            return JsonResponse(data={'error': str(e)}, status=400)

    return JsonResponse(data={'error': 'Неверный тип запроса'}, status=400)



# def send_xlsx_file(request):
#     if request.method == 'GET':
#         today = datetime.today().replace(microsecond=0)
#         last_week = today - timedelta(days=7)
#
#         # Создаем пустой словарь
#         model_data = {}
#
#         # Перебираем роботов и добавляем их данные в соответствующие DataFrame
#         robots = Robot.objects.filter(
#             created__range=[last_week, today]
#         ).order_by('model')
#         print(robots)
#         for robot in robots:
#             print(robot)
#             if robot.model not in model_data:
#                 # Если DataFrame для данной модели отсутствует, создаем его
#                 model_data[robot.model] = pd.DataFrame(
#                     columns=['Модель', 'Версия', 'Количество за неделю'])
#
#             # Добавляем новую строку в DataFrame для текущей модели
#             model_data[robot.model] = pd.concat(
#                 [model_data[robot.model],
#                  pd.DataFrame.from_records([{
#                      'Модель': robot.model,
#                      'Версия': robot.version,
#                  }])
#                  ]
#             )
#
#             model_data[robot.model] = model_data[robot.model].groupby(
#                 ['Модель', 'Версия']
#             ).size().reset_index(name='Количество за неделю')
#             # print(model_data[robot.model])
#         # Записываем каждый DataFrame на отдельный лист
#         with pd.ExcelWriter('multiple.xlsx', engine='xlsxwriter') as writer:
#             for model, df in model_data.items():
#                 df.to_excel(writer, sheet_name=model, index=False)
#
#         return JsonResponse(data={'message': 'Файл загружается'}, status=200)
#
#     return JsonResponse(data={'error': 'Неверный тип запроса'}, status=400)
