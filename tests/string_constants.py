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
