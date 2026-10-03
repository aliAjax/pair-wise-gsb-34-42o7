def create_inspection_result_dto(**overrides):
    row = {"id":1,"task_id":1,"device_id":1,"item_code":"item code 1","result_status":"IN_PROGRESS","measured_value":"measured value 1","photo_url":"/mock/photo_url-1.png","note":"note 1"}
    row.update(overrides)
    return row
