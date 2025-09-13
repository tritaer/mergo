from django.core.management.base import BaseCommand
from aggregator.models import Company, Station, Schedule, AggregationUnit
import logging
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse balance components and insert to DB IEQ if component 2 or cons-gen if component 1'

    def handle(self, *args, **options):
        u1 = User.objects.create_user(username='admin', password='admin', is_staff=True, is_superuser=True)
        u1.save()
        u2 = User.objects.create_user(username='dispatcher', password='dispatcher', is_staff=True, is_superuser=False)
        u2.save()
        u3 = User.objects.create_user(username='generation', password='generation', is_staff=False, is_superuser=False)
        u3.save()
        # add AU
        au1 = AggregationUnit(alias='Полтавська', mms_name='ETG-GE_UA53', w_code='62W217838713880D')
        au1.save()
        au2 = AggregationUnit(alias='Кіровоградська', mms_name='ETG-GE_UA35', w_code='62W305861363013Y')
        au2.save()
        au3 = AggregationUnit(alias='Київська', mms_name='ETG-GE_UA32', w_code='62W655034242062T')
        au3.save()
        au4 = AggregationUnit(alias='Житомирська', mms_name='ETG-GE_UA18', w_code='62W783791382514A')
        au4.save()
        #add company
        c1 = Company(name='ПолтаваГідро', mms_name='POLTAVAHYDRO', x_code='62X941298906788K')
        c1.save()
        c1.users.set([u1, u3])
        c2 = Company(name='ЕкоГідро', mms_name='ECOHYDRO', x_code='62X912568888620T')
        c2.save()
        c2.users.set([u1, u3])
        c3 = Company(name='ГрінГайворон', mms_name='GREENGAIVORON', x_code='62X414281987079I')
        c3.save()
        c3.users.set([u1, u3])
        #add stations
        s1 = Station(alias='СумськаГЕС', mms_name='SUKHORABIVSK-HPP', w_code='62W588326950277I', aggregation_unit=au1, p_min=0, p_max=10000, company=c1)
        s1.save()
        s2 = Station(alias='ОстапивськаГЕС', mms_name='OSTAPYEVSKA-HPP', w_code='62W318034213015V', aggregation_unit=au1, p_min=0, p_max=10000, company=c1)
        s2.save()
        s3 = Station(alias='ОпишнянськаГЕС', mms_name='OPISHNYANSKA-HPP', w_code='62W688616143880I', aggregation_unit=au1, p_min=0, p_max=10000, company=c1)
        s3.save()
        s4 = Station(alias='КунтсівськаГЕС', mms_name='KUNTSIVSKA-HPP', w_code='62W542611445445O', aggregation_unit=au1, p_min=0, p_max=10000, company=c1)
        s4.save()
        s5 = Station(alias='ГайворонГЕС', mms_name='HAYVORON-HPP', w_code='62W1853057999031', aggregation_unit=au2, p_min=0, p_max=10000, company=c2)
        s5.save()
        s6 = Station(alias='БогуславГЕС', mms_name='BOHUSLAV-HPP', w_code='62W1968197202016', aggregation_unit=au3, p_min=0, p_max=10000, company=c3)
        s6.save()
        s7 = Station(alias='ДубентсіГЕС', mms_name='DYBENTSI-HPP', w_code='62W982874386630V', aggregation_unit=au3, p_min=0, p_max=10000, company=c3)
        s7.save()
        s8 = Station(alias='ЧиживськаГЕС', mms_name='CHYZHIVSKA-HPP', w_code='62W231445246939V', aggregation_unit=au4, p_min=0, p_max=10000, company=c3)
        s8.save()
