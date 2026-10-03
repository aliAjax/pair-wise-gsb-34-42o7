from src.seed import seed
class FireDeviceRepository:
    def find_all(self):
        return seed["fireDevice"]
