import mimetypes
import os.path

import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Robot
import json
import pytz
from datetime import datetime, timedelta
from django.utils import timezone


@csrf_exempt
def create_robot(request):
    if request.method == 'POST':
        try:
            # Загрузка данных из тела запроса
            data = json.loads(request.body)
            model = data.get('model')
            version = data.get('version')
            # Преобразование строки 'created' в объект datetime
            dt_obj = datetime.strptime(
                data.get('created'), '%Y-%m-%d %H:%M:%S'
            )
            # Привязка времени к часовому поясу 'Europe/Moscow'
            created = pytz.timezone('Europe/Moscow').localize(dt_obj)

            # Проверка, что робот с такими параметрами не существует в базе данных
            if not Robot.objects.filter(model=model, version=version,
                                        created=created).exists():
                # Создание нового объекта робота в базе данных
                Robot.objects.create(serial=f'{model}-{version}', model=model,
                                     version=version, created=created
                )

                # Возврат JSON-ответа с сообщением об успешном создании робота
                return JsonResponse(
                    data={'message': 'Робот успешно создан'}, status=200
                )
            return JsonResponse(
                data={'message': 'Такой робот уже есть в базе данных'},
                status=200
            )
        # Обработка исключений
        except Exception as e:
            # Возврат JSON-ответа с сообщением об ошибке
            return JsonResponse(data={'error': str(e)}, status=400)

    # Возврат JSON-ответа с сообщением о неверном типе запроса
    return JsonResponse(data={'error': 'Неверный тип запроса'}, status=400)


def send_xlsx_file(request):
    if request.method == 'GET':
        # Получение текущей даты и времени и вычисление даты на неделю назад
        today = timezone.now().replace(microsecond=0)
        last_week = today - timedelta(days=7)

        # Словарь для хранения данных по моделям роботов
        model_data = {}
        # Получение роботов, созданных за последнюю неделю, отсортированных по модели
        robots = Robot.objects.filter(
            created__range=[last_week, today]
        ).order_by('model')

        for robot in robots:
            if robot.model not in model_data:
                # Создание пустого DataFrame для каждой модели робота
                model_data[robot.model] = pd.DataFrame(
                    columns=['Модель', 'Версия', 'Количество за неделю']
                )

            df = model_data[robot.model]
            # Поиск строки с соответствующей версией робота
            version_row = df[(df['Версия'] == robot.version)]
            if version_row.empty:
                # Добавление новой строки в DataFrame, если версия робота не найдена
                df = pd.concat([
                    df,
                    pd.DataFrame.from_records([{
                        'Модель': robot.model,
                        'Версия': robot.version,
                        'Количество за неделю': 1,
                    }])
                ], ignore_index=True)
            else:
                version_row_index = version_row.index[0]
                # Увеличение счетчика количества роботов за неделю, если версия робота уже существует
                df.at[version_row_index, 'Количество за неделю'] += 1
            model_data[robot.model] = df

        # Создание файла Excel с помощью библиотеки pandas
        with pd.ExcelWriter(f'download_file/robots.xlsx',
                            engine='xlsxwriter') as writer:
            for model, df in model_data.items():
                # Запись данных в отдельные листы Excel-файла
                df.to_excel(writer, sheet_name=model, index=False)

        # Получение базовой директории проекта
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Имя файла
        filename = 'robots.xlsx'
        # Полный путь к файлу
        filepath = base_dir + '/download_file/' + filename
        # Открытие файла в режиме чтения байтов
        path = open(filepath, 'rb')
        # Определение MIME-типа файла
        mime_type, _ = mimetypes.guess_type(filepath)
        # Создание HTTP-ответа с файлом
        response = HttpResponse(path, content_type=mime_type)
        # Установка заголовка Content-Disposition для скачивания файла
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response

    # Возврат JSON-ответа с сообщением о неверном типе запроса
    return JsonResponse(data={'error': 'Неверный тип запроса'}, status=400)
