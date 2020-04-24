from datetime import datetime

ALL_USER_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34',
                      '52d7c87f8c26433dbd095048ad30c8cf',
                      '117154df05874f41bfdaebcae6abfe98']
CONSUMPTION = {"2020-01-15 10:00:04": {'power': 27279, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437},
               "2020-01-15 10:01:10": {'power': 27200, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437}}
DISAGGREGATION = {"2020-01-15 10:01:04": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000},
                  "2020-01-15 10:01:10": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000}}
EMPTY_GROUP_CONSUMPTION = {'consumed_energy': {},
                           'consumed_power': {},
                           'group_users': [{'1': {'energy': [], 'power': []}},
                                           {'2': {'energy': [], 'power': []}}],
                           'produced_first_meter_energy': {},
                           'produced_first_meter_power': {},
                           'produced_second_meter_energy': {},
                           'produced_second_meter_power': {}}
EMPTY_RESPONSE = {}
EMPTY_RESPONSE_BYTES = {'energy': {}, 'power': {}}
GROUP_CONSUMPTION = {'consumed_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                         '2020-01-15 10:01:10': 2180256872214000},
                     'consumed_power': {'2020-01-15 10:00:04': 27279,
                                        '2020-01-15 10:01:10': 27200},
                     'group_users': [{'1':
                                      {'energy': [{'2020-01-15 10:00:04': 2180256872214000},
                                                  {'2020-01-15 10:01:10': 2180256872214000}],
                                       'power': [{'2020-01-15 10:00:04': 27279},
                                                 {'2020-01-15 10:01:10': 27200}]}},
                                     {'2':
                                      {'energy': [{'2020-01-15 10:00:04': 2180256872214000},
                                                  {'2020-01-15 10:01:10': 2180256872214000}],
                                       'power': [{'2020-01-15 10:00:04': 27279},
                                                 {'2020-01-15 10:01:10': 27200}]}}],
                     'produced_first_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                     '2020-01-15 10:01:10': 2180256872214000},
                     'produced_first_meter_power': {'2020-01-15 10:00:04': 27279,
                                                    '2020-01-15 10:01:10': 27200},
                     'produced_second_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:01:10': 2180256872214000},
                     'produced_second_meter_power': {'2020-01-15 10:00:04': 27279,
                                                     '2020-01-15 10:01:10': 27200}}
INDIVIDUAL_CONSUMPTION = {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                     '2020-01-15 10:01:10': 2180256872214000},
                          'power': {'2020-01-15 10:00:04': 27279, '2020-01-15 10:01:10': 27200}}
INDIVIDUAL_DISAGGREGATION = {"2020-01-15 10:01:04": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000},
                             "2020-01-15 10:01:10": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000}}
LAST_READING_ONGOING_TERM = bytes(
    '52d7c87f8c26433dbd095048ad30c8cf_' + datetime.today().
    strftime('%Y-%m-%d %H:%M:%S'), encoding='utf-8')
READINGS = [b'{"type": "reading", "values": {"energy": 1512027002819000}}',
            b'{"type": "reading", "values": {"energy": 1512028877416000}}',
            b'{"type": "reading", "values": {"energy": 1512032408202000}}']
READINGS_LAST_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027005000000}}',
    b'{"type": "reading", "values": {"energy": 1512027002819000}}']
READINGS_ONGOING_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027009000000}}',
    b'{"type": "reading", "values": {"energy": 1512027005000100}}']
SORTED_KEYS = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 00:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 01:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 02:00:00']
SORTED_KEYS_LAST_TERM = [
    [b'52d7c87f8c26433dbd095048ad30c8cf_2020-03-11 04:15:00'],
    [b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-12 04:15:00']]
SORTED_KEYS_ONGOING_TERM = [
    [LAST_READING_ONGOING_TERM],
    [b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-12 04:15:00']]
SORTED_KEYS_ALL_TERMS = [[b'52d7c87f8c26433dbd095048ad30c8cf_2019-03-11 01:00:00'],
                         [b'52d7c87f8c26433dbd095048ad30c8cf_2018-03-12 01:00:00'],
                         SORTED_KEYS_ONGOING_TERM[0], SORTED_KEYS_ONGOING_TERM[1]]
SORTED_KEYS_ESTIMATION = [SORTED_KEYS_ALL_TERMS[0],
                          SORTED_KEYS_ALL_TERMS[1]] + SORTED_KEYS_ALL_TERMS
READINGS_ALL_TERMS = [READINGS_LAST_TERM[0], READINGS_LAST_TERM[1],
                      READINGS_ONGOING_TERM[0],
                      READINGS_ONGOING_TERM[1]]
READINGS_ESTIMATION = [READINGS_ALL_TERMS[0],
                       READINGS_ALL_TERMS[1]] + READINGS_ALL_TERMS
SQLALCHEMY_RETURN_VALUES = [(1002846.2290000044,), (896919.8780000011,)]
