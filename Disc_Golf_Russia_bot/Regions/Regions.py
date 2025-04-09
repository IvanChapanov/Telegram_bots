regions = {
    'екатеринбург': {
        'fullname': 'Екатеринбург',
        'shortname': 'Екб',
        'region_channel': 'https://t.me/discgolf_ekb',
        'park': {
            'Уктус': {
                'address': 'г.Екатеринбург, ул.Зимняя, 27',
                'metrix_link': 'https://discgolfmetrix.com/course/32750',
                'latitude': 56.773543,
                'longitude': 60.649179,
                'cources':{
                    'Изумрудный':{
                        'name': 'Изумрудный'
                    },
                    'Рубиновый': {
                        'name': 'Рубиновый'
                    },
                    'Сапфировый': {
                        'name': 'Сапфировый'
                    },
                    'Хрустальный': {
                        'name': 'Хрустальный'
                    }
                }

            },
            'Академический':{
                'address': 'г.Екатеринбург, Преображенский парк',
                'metrix_link': '',
                'latitude': 56.78403654846384,
                'longitude': 60.51555008783605,
                'cources':{
                    'Тренировочный':{
                        'name': 'Тренировочный'
                    }
                }

            }
        }
    }
}


class Region:
    _registry = {}
    def __init__(self, name, **attributes):
        self.name = name
        for key, value in attributes.items():
            setattr(self, key, value)

    @classmethod
    def load_regions(cls, regions_data):
        for name, data in regions_data.items():
            cls._registry[name] = cls(name=name, **data)

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)






