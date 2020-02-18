Required Information
====================

* platform id (int)
* gender ("MALE"/"FEMALE")
* first name (str)
* name (str)
* mail (str)
* meter id (str)
* role ("LOCAL_POWER_TAKER"/"ADMINISTRATOR")
* inhabitants (int)
* flat size (float)
* group meter id (str)

Format
======

* e.g. as JSON object: 
```
{
  "platform_id" => int,
  "gender" => str,
  "first_name" => str, 
  "name" => str, 
  "mail" => str, 
  "meter_id" => str,
  "role" => str, 
  "group_meter_id" => str
}
