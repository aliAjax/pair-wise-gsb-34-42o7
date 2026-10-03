def create_building_dto(**overrides):
    row = {"id":1,"name":"name 1","campus":"campus 1","floor_count":"floor count 1","fire_grade":"fire grade 1","manager_id":1,"address_code":"address code 1"}
    row.update(overrides)
    return row
