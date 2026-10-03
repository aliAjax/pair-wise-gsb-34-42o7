def create_fire_device_dto(**overrides):
    row = {
        "id": 0,
        "building_id": 0,
        "device_code": "",
        "device_type": "HYDRANT",
        "floor": "1",
        "location_desc": "",
        "install_date": "",
        "status": "ACTIVE",
        "base_status": "NORMAL",
        "next_maintenance_at": None,
        "owner_id": None,
    }
    row.update(overrides)
    return row
