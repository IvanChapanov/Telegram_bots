regions = {
    '66': {
        'name': 'Екатеринбург',
        'shortname': 'Екб',
        'region_channel': 'https://t.me/discgolf_ekb'
    }
}

class Region:
    _registry = {}
    def __init__(self, code, **attributes):
        self.code = code
        for key, value in attributes.items():
            setattr(self, key, value)

    @classmethod
    def load_regions(cls, regions_data):
        for code, data in regions_data.items():
            cls._registry[code] = cls(code=code, **data)

    @classmethod
    def get(cls, code):
        return cls._registry.get(code)




