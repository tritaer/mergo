from datetime import datetime
from datetime import timedelta
import pytz
from aggregator.models import Station, Schedule, get_version, AggregationUnit, Company, CommerceReport, get_commerce_version
import xml.etree.ElementTree as ET
from django.conf import settings
from .utils import day_duration



def generate_mrid(date, version):
    return f'62X8344396037694-{date.strftime('%Y%m%d')}-{version}'


def generate_cdt():
    """return UTC now in format YYYY-mm-ddTHH:MM:SSZ"""
    return datetime.now(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def get_process_type(date):
    """Determine the process type based on the date.
    A12 for d-2 and earlier, 
    A01 for d-1 before 15:00 Kyiv time, 
    A02 start from d-1 after 15:00 Kyiv time"""
    #TODO:  A02 d (start from 15:00 d-1) data shoud be same for h - 110min. Only change future hours.
    now_kyiv = datetime.now(pytz.UTC).astimezone(pytz.timezone('Europe/Kyiv'))
    if date.date() - now_kyiv.date() > timedelta(days=1):
        return 'A12'
    elif now_kyiv.hour < 15 and date.date() - now_kyiv.date() == timedelta(days=1):
        return 'A01'
    else:
        return 'A02'


def prs_date(date):
    """take date datetime.datetime and return start date as date in UTC in format YYYY-mm-ddTHH:MMZ"""
    start = pytz.timezone('Europe/Kyiv').localize(date).astimezone(pytz.UTC)
    stop = pytz.timezone('Europe/Kyiv').localize(date + timedelta(days=1)).astimezone(pytz.UTC)
    return start.strftime('%Y-%m-%dT%H:%MZ'), stop.strftime('%Y-%m-%dT%H:%MZ')


def add_ts(root, unit, data, start, stop, ts_n, business_type, duration, direction=None):  # root - xml root, unit - AU (station), hours - dict of hours, start, stop - time interval, ts_n - ts mrid, direction - direction of flow
    ts = ET.SubElement(root, 'PlannedResource_TimeSeries')
    ET.SubElement(ts, 'mRID').text = f'TS{ts_n}'
    ET.SubElement(ts, 'businessType').text = business_type  # A01 produce, A04 consume, A60 min, A61 max, A95 FCR, A96 aFRR, A97 mFRR, A98 RR
    if direction is not None:
        ET.SubElement(ts, 'flowDirection.direction').text = direction
    ET.SubElement(ts, 'product').text = '8716867000016'
    ET.SubElement(ts, 'connecting_Domain.mRID', {'codingScheme': 'A01'}).text = '10Y1001C--000182'
    ET.SubElement(ts, 'registeredResource.mRID', {'codingScheme': 'A01'}).text = unit
    ET.SubElement(ts, 'resourceProvider_MarketParticipant.mRID', {'codingScheme': 'A01'}).text = settings.COMPANY_X
    ET.SubElement(ts, 'measurement_Unit.name').text = 'MAW'
    sp = ET.SubElement(ts, 'Series_Period')
    ti = ET.SubElement(sp, 'timeInterval')
    ET.SubElement(ti, 'start').text = start
    ET.SubElement(ti, 'end').text = stop
    ET.SubElement(sp, 'resolution').text = 'PT15M'
    if type(data) == list:
        for i, value in enumerate(data):
            for j in range(1, 5):
                point = ET.SubElement(sp, 'Point')
                ET.SubElement(point, 'position').text = str(i * 4 + j)
                ET.SubElement(point, 'value').text = str(value / 1000)
    else:
        for i in range(duration*4):
            point = ET.SubElement(sp, 'Point')
            ET.SubElement(point, 'position').text = str(i + 1)
            ET.SubElement(point, 'value').text = str(data / 1000)


def save_prs_xml(report_data, date, duration, version=None):
    # TS for now its A01 for each AU.
    # TODO: A04, A60/A61 for consumption, AS (A95...)
    # unique data for PRS is report_data, date, version, cdt
    if version is None:
        version = 1  # Or get the correct version as needed

    filename = f'/Users/tritaer/programing/mergo/data/PRS_ETG-AGG_d_{date.strftime("%Y.%m.%d")}_IPS_v{version}.xml'
    start, stop = prs_date(date)
    print(start, stop)
    root = ET.Element('PlannedResourceSchedule_MarketDocument',
                      {'xmlns': 'urn:iec62325.351:tc57wg16:451-7:plannedresourcescheduledocument:6:0',
                       'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                       'xsi:schemaLocation': 'urn:iec62325.351:tc57wg16:451-7:plannedresourcescheduledocument:6:0 ../../xsd/iec62325-451-7-plannedressourceschedule_v6_0.xsd'})
    ET.SubElement(root, 'mRID').text = generate_mrid(date, version)
    ET.SubElement(root, 'revisionNumber').text = str(version)
    ET.SubElement(root, 'type').text = 'A14'
    ET.SubElement(root, 'process.processType').text = get_process_type(date)
    ET.SubElement(root, 'sender_MarketParticipant.mRID', {'codingScheme': 'A01'}).text = settings.COMPANY_X
    ET.SubElement(root, 'sender_MarketParticipant.marketRole.type').text = 'A27'
    ET.SubElement(root, 'receiver_MarketParticipant.mRID', {'codingScheme': 'A01'}).text = '10X1001C--00001X'
    ET.SubElement(root, 'receiver_MarketParticipant.marketRole.type').text = 'A04'
    ET.SubElement(root, 'createdDateTime').text = generate_cdt()
    sp = ET.SubElement(root, 'schedule_Period.timeInterval')
    ET.SubElement(sp, 'start').text = start
    ET.SubElement(sp, 'end').text = stop
    ts_n = 0
    for unit, data in report_data.items():
        ts_n += 1
        # A01 production
        add_ts(root, unit, data['schedule'], start, stop, ts_n, 'A01', duration)
        # A60 min
        add_ts(root, unit, data['max'], start, stop, ts_n, 'A60', duration, 'A01')
        # A61 max
        add_ts(root, unit, data['min'], start, stop, ts_n, 'A61', duration, 'A01')
    tree = ET.ElementTree(root)
    ET.indent(tree)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f'PRS XML saved to {filename}')



def generate_prs(date: datetime):
    # PRS are generated per aggregation unit
    # Get all stations for the date
    stations = Station.objects.filter(schedule__date=date).distinct()
    au = AggregationUnit.objects.all()
    report_data = {}
    duration = day_duration(date)
    # Initialize report data for each AU
    for unit in au:
        report_data[unit.w_code] = {'schedule': [0 for _ in range(duration)], 'max': 0, 'min': 0}
    # Fill report data for each AU
    for station in stations:
        # Get the latest schedule for the station
        schedule = Schedule.objects.filter(station=station, date=date).order_by('-version').first()
        if schedule:
            # Generate PRS for the station
            print(f'Add to PRS {station.mms_name} on {date} (v{schedule.version})')
            print(f'schedule: {len(schedule.schedule)}, data: {len(report_data[station.aggregation_unit.w_code]["schedule"])}')
            for hour, value in schedule.schedule.items():
                report_data[station.aggregation_unit.w_code]['schedule'][int(hour)] += value
            report_data[station.aggregation_unit.w_code]['max'] += station.p_max
            report_data[station.aggregation_unit.w_code]['min'] += station.p_min
            
    print('PRS data:')
    for unit, data in report_data.items():
        print(f'Aggregation Unit: {unit}, Data: {data}')
    # TODO: save PRS data to DB with version
    # data need to be saved in DB?
    save_prs_xml(report_data, date, duration)


