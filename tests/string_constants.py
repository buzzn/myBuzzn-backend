from datetime import datetime, timedelta
from models.per_capita_consumption import PerCapitaConsumption


ALL_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34', '52d7c87f8c26433dbd095048ad30c8cf',
                 '117154df05874f41bfdaebcae6abfe98', '0a0f65e992c042e4b86956f3f080114d',
                 '5e769d5b83934bccae11a8fa95e0dc5f', 'e2a7468f0cf64b7ca3f3d1350b893c6d']

ALL_USER_METER_IDS = ['b4234cd4bed143a6b9bd09e347e17d34',
                      '52d7c87f8c26433dbd095048ad30c8cf',
                      '117154df05874f41bfdaebcae6abfe98']

COMMUNITY_SAVING = ('2020-02-13 16:20:21.977425', 85184267259376.5)

COMMUNITY_SAVING_DICT = {'2020-02-13 16:20:21': 85184267259376.5}

CONSUMPTION = {"2020-01-15 10:00:04": {'power': 27279, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437},
               "2020-01-15 10:01:10": {'power': 27200, 'power3': -27279,
                                       'energyOut': 0, 'power1': 0,
                                       'energy': 2180256872214000,
                                       'power2': -2437}}

DAY_ONE = datetime.today() - timedelta(days=1)

DAY_TWO = datetime.today()

DAY_ZERO = datetime.today() - timedelta(days=2)

BASE_VALUES = PerCapitaConsumption(DAY_ZERO, ALL_USER_METER_IDS[1],
                                   0.0, 0.0, 2, 0.0, 0.0, 0, 0.0, 0)

DISAGGREGATION = {"2020-01-15 10:01:04": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000},
                  "2020-01-15 10:01:10": {"Durchlauferhitzer-1": 0,
                                          "Grundlast-1": 50000000}}

EMPTY_GROUP_CONSUMPTION = {'consumed_energy': {},
                           'consumed_power': {},
                           'group_users': {'1': {'energy': {}, 'power': {}},
                                           '2': {'energy': {}, 'power': {}}},
                           'produced_first_meter_energy': {},
                           'produced_first_meter_power': {},
                           'produced_second_meter_energy': {},
                           'produced_second_meter_power': {}}

AVERAGE_POWER = {'2020-01-15 10:15:00': 224550.0,
                 '2020-01-15 10:30:00': 232000.0,
                 '2020-01-15 10:45:00': 227630.0}

FIRST_LAST_ENERGY = {'2020-01-15 10:00:04': 2180256872214000,
                     '2020-01-15 10:47:10': 2180256872214000}

FIRST_LAST_METER_READING_DATE = [{"type": "reading",
                                  "values": {"power": 126430, "power3": 13330, "energyOut": 0,
                                             "power1": 26980, "energy": 198360858657000, "power2":
                                                 86120},
                                  "time": "2020-04-28 06:56:00"},
                                 {"type": "reading",
                                  "values": {"power": 126430, "power3": 13330, "energyOut": 0,
                                             "power1": 26980, "energy": 198382608371000, "power2":
                                                 86120},
                                  "time": "2020-04-28 06:56:00"}]

FIRST_METER_READING_DATE = '{"type": "reading", "values": {"energy": 198360858657000.00}}'

FIRST_ENERGY_DATE = 198360858657000

LAST_METER_READING_DATE = '{"type": "reading", "values": {"energy": 198382608371000.00}}'

LAST_ENERGY_DATE = 198382608371000

EMPTY_RESPONSE = {}

EMPTY_RESPONSE_BYTES = {'energy': {}, 'power': {}}

GROUP_CONSUMPTION = {'consumed_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                         '2020-01-15 10:47:10': 2180256872214000},
                     'consumed_power': {'2020-01-15 10:15:00': 224550.0,
                                        '2020-01-15 10:30:00': 232000.0,
                                        '2020-01-15 10:45:00': 227630.0},
                     'group_users': {'1': {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:47:10': 2180256872214000},
                                           'power': {'2020-01-15 10:15:00': 224550.0,
                                                     '2020-01-15 10:30:00': 232000.0,
                                                     '2020-01-15 10:45:00': 227630.0}},
                                     '2': {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:47:10': 2180256872214000},
                                           'power': {'2020-01-15 10:15:00': 224550.0,
                                                     '2020-01-15 10:30:00': 232000.0,
                                                     '2020-01-15 10:45:00': 227630.0}}},
                     'produced_first_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                     '2020-01-15 10:47:10': 2180256872214000},
                     'produced_first_meter_power': {'2020-01-15 10:15:00': 224550.0,
                                                    '2020-01-15 10:30:00': 232000.0,
                                                    '2020-01-15 10:45:00': 227630.0},
                     'produced_second_meter_energy': {'2020-01-15 10:00:04': 2180256872214000,
                                                      '2020-01-15 10:47:10': 2180256872214000},
                     'produced_second_meter_power': {'2020-01-15 10:15:00': 224550.0,
                                                     '2020-01-15 10:30:00': 232000.0,
                                                     '2020-01-15 10:45:00': 227630.0}}

GROUP_LAST_READING = {'type': 'reading',
                      'values': {'energyOut': 2189063000, 'energy2': 0,
                                 'energy1': 0, 'voltage1': 231000,
                                 'voltage2': 231900, 'voltage3': 231500,
                                 'energyOut1': 0, 'power': 21520,
                                 'energyOut2': 0, 'power3': 0, 'power1': 1700,
                                 'energy': 2466839634000, 'power2': 19820}}

GROUP_MEMBERS = [{'id': 1, 'meter_id': ALL_USER_METER_IDS[0],
                  'inhabitants': 2},
                 {'id': 2, 'meter_id': ALL_USER_METER_IDS[1],
                  'inhabitants': 2},
                 {'id': 3, 'meter_id': ALL_USER_METER_IDS[2],
                  'inhabitants': 2}]

GROUP_PRODUCTION_METER_IDS = (
    '5e769d5b83934bccae11a8fa95e0dc5f', 'e2a7468f0cf64b7ca3f3d1350b893c6d')

GROUPMEMBER1_LAST_READING = {'type': 'reading',
                             'values': {'power': 20032100, 'power3': -2730,
                                        'energyOut': 0, 'power1': -173960,
                                        'energy': 3603609657330000, 'power2': -5900}}

GROUPMEMBER1_WEBSOCKET_DATA = {'id': 1, 'meter_id': 'b4234cd4bed143a6b9bd09e347e17d34',
                               'consumption': 3603609657330000, 'power': 20032100}

GROUPMEMBER2_LAST_READING = {'type': 'reading',
                             'values': {'power': 734100, 'power3': 35180,
                                        'energyOut': 0, 'power1': 125670,
                                        'energy': 190585532038000, 'power2': 26720}}

GROUPMEMBER3_LAST_READING = {'type': 'reading',
                             'values': {'power': 5877540, 'power3': 1361800,
                                        'energyOut': 0, 'power1': 1410390,
                                        'energy': 1500976759905000, 'power2': 1388390}}

# pylint:disable=line-too-long
SAMPLE_AVATAR = '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCACWAJYDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5/ooooAKKKKACiiigAooooAXvS88UvTmtaewC6RFcx844YiplJRtfqb0aE6qk4/ZVzH5zR0pyqXYAdTVq8tBamNc5YgFh6U7q9jNU5OLmtkUqKKKZAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQA48+tOWN3YBFJJ7AVoabprXb7mB2ZwAO5ro1srWxh3TsEHotc9XExg+Vas9nA5NVxMPayfLHuzmfsBU753ESnt1P5CtrRvJkgktNzOGB+8uOajk1bTrfm3tfMOerVPpesi7uxEYUjBHGB3rGrKpKDfKenl9HB0cVGCqpt6bN3v56L8Crp+lRJfhmcny/mIKkVW1G2luLp549rgnoh5H4V1U7xwoXkC7DwW9Kzp9PG3zYiGU9Cpwayp4luXNI7sZk8I0fYU+ju7b+Xc45lZTyOaaa6C5tkdcTLkdBIByPr61j3Nq1u2Dyp+6w6Gu+FRSPkcThJ0H5FaiiitDjCiiigAooooAKKKKACiiigB1WrCya+uViTv1PpVYAmur0y3/s/Tjclf3r4A4rKvU9nHTdnpZZgvrVa0vhjq/QtvNbaLZeXySB0HrXJ3l/NfTF5GOOw9Ku6/ceZdqinhVGfqRzWQBk45NZYeiorne7OzOcwlVqfVqelOGiSG5q9pbsmoRMv3s1U2/1rU0SHdO0xHCDj61tUaUHc8zAwlPEwUe/5HQa9G8mmMUz8pyRXOabq0tgdpO+M9VNdXFJHdWLAkFeVOa4m9ga2unjPBB6GuPCJSi6UkfTcQSnSrU8bQlujqGaKSL7TABLA334+61nXHl2zBWXzLRzlT/dPpWfp9/JYXG4ZKHhl9RW5cWcc9uXhw1vLz7oapx9lKz2MYV/r9Fypr31uv66Pquhzt3D5UwZPuP8y/Sq/PNaU8JNkysPngb9DWbycV1xd0fOYinyT23/AK/MZRRRVnOFFFFABRRRQAUUUUAXtNtjcXqA/dByfpXVXsvl28aEjCqCf6Vh6MpCu+BlmCjNaOpZe5kTgKzqvSuCv79VLsfWZa1hsBKa3l/wbfkYOptuvn9sD9Ko1ZuzuvJSOm41X9K7YK0Uj5nES56spd2xee9dHDjT/DxkPDy9P8RWHaRGe6ji/vGtTxDcBZI7NMbIhzj1rKt70ow+Z6WXv2FCrinvblXq/wDgEvhy63SS27H7/K59aXXrQyRrdqPnX5ZPrWNYztbXaSj+E811c8kYmG/BgulwfY1jUTp1VNdT0cBOGLy+WHqPWL+6+z+/T5nFjmtrQ9RNvOIZP9XJ+lZ9/aNZ3TxN26H1qurMrAjtXTKMasLdzwqFargsQpLRxep1l3Z7Jyw5DrtPuD0rlJkMcro3UHFdhbXC3mlxyt95flaud1iLZdlgMB+cY6HvXPhptScJHtZ3QpypRxFLZ6/eZlFFFdh8yFFFFAFmNIi2JZCg9QtW0srOQ/LeqPQMpFZuaM1Li3szenVhFWlBP7/8zVGjM5HlXELZ/wBrFMGh3h5RA30INUF3H7u78KsxG9Q4jEnPbmofOtmdMHhp/FTfyf8AwDWsrWa2gjWWNlImyeKu6muLjcR0O79Kq2tzeCzZm3iRWGBjqK07+6aG1FwEVl29CuefSuKo5e0R9RhqdB4SSV0kk9V2ucUytkkg0zFbB1WBxiXT0PuODQLjSJB81vJGx9G4FdvPJbxPl3hKUn7lVfO6/QdoEX+kyTsBiIbufWs2eUz3DyMSSTzXVW1pbQ6XL5cpVJsfMw5FZf8Awjxc/urmN89O1YwrQc5SZ6eJy3ELDUqNNX3bs112/Awt3Pt6V0lm39oaK0I/1kPK+uKzpdBvoicRbgP7pzU2kefY36rKhEbcMOauq4zheL1Wpy4GlWw1fkrQajLR6dx14v8AaGlpcgfvYflesXk966OBBZ6zNauP3U4wMisO+ga1vJIfRqdGSvyr1QsyoS5VWe6fLL1XX5ovaZeeTZ3cZJwVBHsc1Fqr+b5MwJ2uvr371nnK8AnB61I8zNAkZ6ISR+NVyJT5kcrxkpYf2EtktPvv+pXooorU4QooooAKKKKALMdzNCP3bso64q2mt3yHPmZ+oFZv4CkqXCL3RvTxNal8EmvmdFbeJLhplWYJtJ646VuWt39pSQOi5TqtcEDg8V0ei3iyfu3OHAwPcVxYnDxUeaKPpMnzivOqqVad79yR9W0wttktCMHmljbRLpgBEQ57AVj6vCYr9xtwDytT6HCXuHkPRP5mrdKKp88W/vMoY+vPF/V6kIvW2sUdFdJaSWi28k2xO1Zi6Lb7s29+BjnJNUddmzcpEDgKvOPWspS2ep/ClRoyULqW5WY5pQeIcZ0U+XS92jrE0+9QLtv0kUHhTVlYb4Ebwj+5IP8AOuLW4lU/LIw/Gpk1G7T7s70Sw031X3BRzvDQ+xJf9vX/ADO1e2EwR3hUyL3ziq1/osV+4l3GOTGPWsvSNRnndo5ZSWI+UmrMN3cMk8THM0fI46iub2VWnLR7HtLHYHF0Vz021L03Xp1KU3hm4X/VOGH5VQl0a9h+9C2Ktr4gmDfMgNaMerKYVkkiKqTjPaunnxEPiVzw/q+UYhv2cnE5l4ZU+9Ew+tR49q66S+RhnyS49Vwazpb3TZch4DnvgYNaQrye8TjxGWUIfBWXzVjn6Kc2Nxx07UV0nijaKKKACiiigB3c1PbXBt51kHUVX5zQKTV1ZlQk4SUo7o6yaGLVrNXR/mA4PofSmWNubS3CyYzksc+1Zmj3zQyGEk4YjH1rflUTwkBgpZcZrz6ilTfI9j7PBypYuP1qK/eJWfmcndzG4ndyep6mq/er8uk3SSEBQR67hURsLrvEa7ozhbRnylXD4jnbnF39Cr+dGfrVn7Bc/wDPJvyqWPS53OWARe5NNziupEcNWk7KLILWVoLhZF6qa3pZAk8N4hHluNr4rMn+z2iNHFiSXGGZhwPpVzSj9otXt5QdoOcnpWFXVc56uX3jJ4a+r1Xk1/WpV+wNLqZiA+TOSfQVHqcwkuRGnCR/KK3NQuBaQPJEPnPGfSuUZi7Fjzk06MnU959CczpU8JejB3cnd+nRCq7IcqSCPenyTyTAb23Y7kc/nUP4UfhW9kePzO1riUUUUyQooooAKKKKACiiigC7pyF72MehzWxdXq2zqrDIPJx2rP0dAZnYj7o4qDUZfMvHx0HArnlFTq2fQ9mhXlhcFzw3kzahuoLgYVgT3B4NRvaOWzBMyexORXPZZWyCQa0bXV5YsCQb19e9S6Eo6wZrTzOlXtHEq3miyyaohwkisPXA/rTfsV7cD99PtB6rQ2tR4+WIk+5qvLq8z8IAn0FEY1H0SKq1cEt6kpLtdl+PTLeEZYFiO5NTRzwncI2AVOpHQVgS3U0o2tIxX61CrHsTn2p+xcviZiszp0mvYU7L8To5cXUDBSWWReD7j/P6Vzv3cj0rS0u4OTbsepyufWoNSh8u6JAwr/MKqmuSTgZ4yX1ijHELfZ/1/W5Qooorc8kKKKKACiiigAooooAKKKKANvTc21lNOeh/p/8ArrILZcn3q416P7OFsFIYdT+Oao44FRGLTbZ2YmrGVOnTg9Evxe42iiirOMKKKKACiiigCRGaNww4wc5rUuiL6wWZR+8T71Zh3Y5HepbW6a3ZhjcjDDLUTjezW6OvD1lBSpz+GX9JlWig8mirOQKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//Z'

GROUP_PROFILE_PICTURES = [{'id': 1, 'avatar': SAMPLE_AVATAR},
                          {'id': 2, 'avatar': SAMPLE_AVATAR},
                          {'id': 3, 'avatar': SAMPLE_AVATAR}]

INDIVIDUAL_BASELINE = 19361634120995

INDIVIDUAL_CONSUMPTION = {'energy': {'2020-01-15 10:00:04': 2180256872214000,
                                     '2020-01-15 10:47:10': 2180256872214000},
                          'power': {'2020-01-15 10:15:00': 224550.0,
                                    '2020-01-15 10:30:00': 232000.0,
                                    '2020-01-15 10:45:00': 227630.0}}

INDIVIDUAL_DISAGGREGATION = {"2020-01-15 10:01:04": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000},
                             "2020-01-15 10:01:10": {'Durchlauferhitzer-1': 0,
                                                     'Grundlast-1': 50000000}}

INDIVIDUAL_GLOBAL_CHALLENGE = {'baseline': 19361634120995,
                               'saving': {'2020-02-13 09:57:03.620809': 3148577026610.7812}}

INDIVIDUAL_SAVING = ('2020-02-13 09:57:03.620809', 3148577026610.7812)

INDIVIDUAL_SAVING_DICT = {'2020-02-13 09:57:03.620809': 3148577026610.7812}

KEY1_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:02:00'

KEY1_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:02:00'

KEY2_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:07:00'

KEY2_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:07:00'

KEY3_DAY_ONE = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_ONE.strftime('%Y-%m-%d') + ' 12:40:00'

KEY3_DAY_TWO = '52d7c87f8c26433dbd095048ad30c8cf_' + \
    DAY_TWO.strftime('%Y-%m-%d') + ' 12:40:00'

LAST_READING_ONGOING_TERM = bytes(
    '52d7c87f8c26433dbd095048ad30c8cf_' + datetime.today().
    strftime('%Y-%m-%d %H:%M:%S'), encoding='utf-8')

MEMBER_WEBSOCKET_DATA = [{'id': 1, 'meter_id': 'b4234cd4bed143a6b9bd09e347e17d34',
                          'consumption': 3603609657330000, 'power': 20032100},
                         {'id': 2, 'meter_id': '52d7c87f8c26433dbd095048ad30c8cf',
                          'consumption': 190585532038000, 'power': 734100},
                         {'id': 3, 'meter_id': '117154df05874f41bfdaebcae6abfe98',
                          'consumption': 1500976759905000, 'power': 5877540}]

PCC_DAY_ONE = PerCapitaConsumption(DAY_ONE, ALL_USER_METER_IDS[1], 2.1749714, 2.1749714, 2,
                                   1.0874857, 1.0874857, 1, 1.0874857, 397)

PCC_DAY_TWO = PerCapitaConsumption(DAY_TWO, ALL_USER_METER_IDS[1], 1.5, 3.6749714, 2, 0.75,
                                   1.8374857, 2, 0.91874285, 335)

READING = {'time': 1585177200000, 'values': {'power': 5727055, 'power3': 1898229,
                                             'energyOut': 0, 'power1': 1917350,
                                             'energy': 1551192369639000, 'power2': 1900643}}

READING_NEGATIVE_POWER = {'time': 1584572400000, 'values': {'power': -4784541, 'power3': 1583777,
                                                            'energyOut': 0, 'power1': 1599778,
                                                            'energy': 1541570917834000,
                                                            'power2': 1589981}}

READINGS = [b'{"type": "reading", "values": {"energy": 1512027002819000}}',
            b'{"type": "reading", "values": {"energy": 1512028877416000}}',
            b'{"type": "reading", "values": {"energy": 1512032408202000}}']

READINGS_LAST_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027005000000}}',
    b'{"type": "reading", "values": {"energy": 1512027002819000}}']

ENERGY_CONSUMPTION_LAST_TERM = 2181000

READINGS_ONGOING_TERM = [
    b'{"type": "reading", "values": {"energy": 1512027009000000}}',
    b'{"type": "reading", "values": {"energy": 1512027005000100}}']

ENERGY_CONSUMPTION_ONGOING_TERM = 3999900

SORTED_KEYS = [b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 00:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 01:00:00',
               b'52d7c87f8c26433dbd095048ad30c8cf_2020-02-07 02:00:00']

SORTED_KEYS_DAY_ONE = [bytes(KEY1_DAY_ONE, 'utf-8'), bytes(
    KEY2_DAY_ONE, 'utf-8'), bytes(KEY3_DAY_ONE, 'utf-8')]

SORTED_KEYS_DAY_TWO = [bytes(KEY1_DAY_TWO, 'utf-8'), bytes(
    KEY2_DAY_TWO, 'utf-8'), bytes(KEY3_DAY_TWO, 'utf-8')]

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

SQLALCHEMY_RETURN_VALUES = [(1002846.2290000044,), (896919.8780000011,)]

USER_CONSUMPTION_DAY_ONE_ITERATION_FIRST = [
    None,
    b'{"type": "disaggregation", "values": {"Durchlauferhitzer-1": 0, "Grundlast-1": 50000000}}',
    b'{"type": "reading", "values": {"energy": 198360858657000}}']

USER_CONSUMPTION_DAY_ONE_ITERATION_LAST = [
    None,
    b'{"type": "disaggregation", "values": {"Durchlauferhitzer-1": 0, "Grundlast-1": 50000000}}',
    b'{"type": "reading", "values": {"energy": 198382608371000}}']

USER_CONSUMPTION_DAY_ONE = [
    b'{"type": "reading", "values": {"energy": 198382608371000}}',
    b'{"type": "reading", "values": {"energy": 198360858657000}}']

USER_CONSUMPTION_DAY_ONE_TWICE = USER_CONSUMPTION_DAY_ONE +\
    USER_CONSUMPTION_DAY_ONE

USER_CONSUMPTION_DAY_TWO = [
    b'{"type": "reading", "values": {"energy": 198400000000000}}',
    b'{"type": "reading", "values": {"energy": 198385000000000}}']

USER_CONSUMPTION_DAY_TWO_TWICE = USER_CONSUMPTION_DAY_TWO +\
    USER_CONSUMPTION_DAY_TWO

WEBSOCKET_DATA = {"date": 1584534049261,
                  "group_production": 43040,
                  "group_users": [{"id": 1, "meter_id": "b4234cd4bed143a6b9bd09e347e17d34",
                                   "consumption": 3603609657330000, "power": 20032100},
                                  {"id": 2, "meter_id": "52d7c87f8c26433dbd095048ad30c8cf",
                                   "consumption": 190585532038000, "power": 734100},
                                  {"id": 3, "meter_id": "117154df05874f41bfdaebcae6abfe98",
                                   "consumption": 1500976759905000, "power": 5877540}]}

READINGS_ALL_TERMS = [READINGS_LAST_TERM[0], READINGS_LAST_TERM[1],
                      READINGS_ONGOING_TERM[0],
                      READINGS_ONGOING_TERM[1]]

READINGS_ESTIMATION = [READINGS_ALL_TERMS[0],
                       READINGS_ALL_TERMS[1]] + READINGS_ALL_TERMS
