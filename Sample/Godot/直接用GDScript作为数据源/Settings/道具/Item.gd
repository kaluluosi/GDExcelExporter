
extends Reference

static func data():
    var None = null

    data = \
    { 1.0: { 'desc': None,
         'id': 1.0,
         'name': '金币',
         'overlap': -1.0,
         'sell_price': None,
         'type': '虚拟道具',
         'use_effect': False},
  10001.0: { 'desc': '飞蝗石，可以扔向敌人',
             'id': 10001.0,
             'name': '石头',
             'overlap': 100.0,
             'sell_price': 1.0,
             'type': '消耗品',
             'use_effect': 2.0}}
    return data
