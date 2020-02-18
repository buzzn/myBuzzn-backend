Required Information
====================

* platform id (int)
* gender ("MALE"/"FEMALE"/"OTHER"/"UNKNOWN")
* first name (str)
* name (str)
* mail (str)
* meter id (str)
* role ("LOCAL_POWER_TAKER"/"ADMINISTRATOR")
* group meter id (str)

Format
======

* e.g. as JSON object: 
```
{
  "id_platform" => int,
  "gender" => (MALE|FEMALE|OTHER|UNKNOWN),
  "first_name" => str, 
  "name" => str, 
  "mail" => str, 
  "meter_id" => str,
  "role" => (LOCAL_POWER_TAKER|ADMINISTRATOR),
  "group_meter_id" => str
}
