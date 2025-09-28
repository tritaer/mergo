import openpyxl
from datetime import datetime, timedelta
import pytz
from .utils import day_duration
from aggregator.models import Station, Schedule, get_version, get_commerce_version


def save_if_changed(station, date, schedule_data, user):
    previous_schedule = Schedule.objects.filter(station=station, date=date).order_by('-version').first()
    if previous_schedule and previous_schedule.schedule == schedule_data:
        print(f'No changes detected for {station.alias} on {date}. Skipping schedule saving')
        return
    else:
        version = get_version(station, date)
        print(f'Saving schedule for {station.alias} on {date} (v{version})')
        schedule = Schedule(
            station=station,
            date=date,
            version=version,
            schedule=schedule_data,
            created_by=user
        )
        schedule.save()


def upload_schedule(file, user):
    """
    Uploads schedule from file.
    :param file: file with schedule
    :return: result of upload (success or error message)
    """
    # TODO: check if date not over deadline
    # read excel file
    if not file.name.endswith('.xlsx'):
        return 'File must be an Excel (.xlsx) file.'

    wb = openpyxl.load_workbook(file)
    ws = wb['data']
    # check if have authority to upload for station (and station exists)
    # check if not over deadline
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_num = 2
        station = Station.objects.filter(mms_name__iexact=row[0]).first()
        if not station:
            return f'Station {row[0]} in row {row_num} not found'
        # check if user has authority to upload for station
        if user.is_generation and station.company.users.filter(pk=user.pk).count() == 0:
            print(f'U shall not pass')
            return f'User {user.username} is not an authority for station {station.alias}'
        # str to datetime
        date = row[1]
        if type(date) != datetime:
            return f'Invalid date {date} in row {row_num}'
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        # check deadline (d-1 9:00 Kyiv time)
        if date.replace(hour=9, minute=0, second=0, microsecond=0) - timedelta(days=1) < datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Kyiv')).replace(tzinfo=None):
            return f'Date {date.strftime('%Y-%m-%d')} is pass deadline'
        duration = day_duration(date)
        # read schedule data
        schedule_data = {}
        for i in range(duration):
            val = row[i + 2]
            if val is None:
                # val in not None
                err_msg = f'Invalid schedule for {station.alias} on {date.strftime("%Y-%m-%d")}. Value at hour {i} is None.'
                print(err_msg)
                return err_msg
            elif type(val) != int:
                # val is int
                err_msg = f'Invalid schedule for {station.alias} on {date.strftime("%Y-%m-%d")}. Value at hour {i} is not integer.'
                print(err_msg)
                return err_msg
            elif val > station.p_max:
                # val is not greater than station max
                err_msg = f'Invalid schedule for {station.alias} on {date.strftime("%Y-%m-%d")}. Value at hour {i} is greater than station max.'
                print(err_msg)
                return err_msg
            elif val < station.p_min:
                # val is not less than station min
                err_msg = f'Invalid schedule for {station.alias} on {date.strftime("%Y-%m-%d")}. Value at hour {i} is less than station min.'
                print(err_msg)
                return err_msg
            else:
                schedule_data[str(i)] = val
        save_if_changed(station, date, schedule_data, user)
        row_num += 1
    return 'Success'
