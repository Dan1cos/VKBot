import random
import requests
import vk_api
import json
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlite3
import time
from urllib import request
import hashlib

conn = sqlite3.connect("db.db.txt")
c = conn.cursor()
def CheckDBMoney(user_id):
    c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    result = result[0]
    return result
def CheckDBMoneyDonate(user_id):
    c.execute("SELECT moneydonate FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    result = result[0]
    return result
def CheckDBMoneyProduce(user_id):
    c.execute("SELECT moneyproduce FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    return result
def CheckDB(user_id):
    c.execute("SELECT * FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    if result is None:
        return False
    else:
        return True
def RegisterDB(user_id):
    c.execute("INSERT INTO users(user_id, money, timeStart, timeEnd, moneydonate, moneyproduce, realdonate) VALUES (%d,2000,0, 1000000,0,0,0)" % user_id)
    conn.commit()
    c.execute("INSERT INTO animals(user_id,lvl1,lvl2,lvl3,lvl4,lvl5,lvl6,lvl7) VALUES (%d,1,0,0,0,0,0,0)" % user_id)
    conn.commit()
    c.execute("INSERT INTO Time(user_id, TimeRequest) VALUES (%d,%d)" % (user_id, time.time()))
    conn.commit()
    c.execute("INSERT INTO ref(user_id, code, Referals) VALUES (%d,%s,%d)" % (user_id, user_id, 0))
    conn.commit()
    c.execute("INSERT INTO donate(user_id, summ) VALUES (%d,0)" % user_id)
    conn.commit()
    c.execute("INSERT INTO quest(user_id, quest) VALUES (%d,0)" % user_id)
    conn.commit()
def UpadateDBMoney(user_id, donate):
    c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
    Donate = c.fetchone()
    OldDonate = Donate[0]
    NewDonate = int(OldDonate) + int(donate)
    c.execute("UPDATE users SET money = '%d' WHERE user_id = %d" %(int(NewDonate),user_id))
    conn.commit()
def UpdateDBMoneyDec(user_id, amount):
    c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
    Old = c.fetchone()
    Old = Old[0]
    NewAmount = int(Old) - int(amount)
    c.execute("UPDATE users SET money = '%d' WHERE user_id = %d" %(int(NewAmount),user_id))
    conn.commit()
def UpdateTime(user_id,time):
    c.execute("UPDATE users SET timeStart = '%d' WHERE user_id = %d " % (time,user_id))
    conn.commit()
def CheckTime(user_id, time):
    c.execute("SELECT timeStart FROM users WHERE user_id = %d" % user_id)
    Time = c.fetchone()
    Time = Time[0]
    TimeRes = time - Time
    return TimeRes
def CanAfford(user_id, amount, NameofAnimal):
    c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    if result[0] >= amount:
        collect = int(ProducedbyTime(user_id, "lvl1", time.time())) + int(
            ProducedbyTime(user_id, "lvl2", time.time())) + int(
            ProducedbyTime(user_id, "lvl3", time.time())) + int(
            ProducedbyTime(user_id, "lvl4", time.time())) + int(
            ProducedbyTime(user_id, "lvl5", time.time())) + int(
            ProducedbyTime(user_id, "lvl6", time.time())) + int(
            ProducedbyTime(user_id, "lvl7", time.time()))
        UpdateTimeRequest(user_id, time.time())
        UpadateDBMoneyProduce(user_id, collect)
        c.execute("SELECT %s FROM animals WHERE user_id = %d" % (NameofAnimal,user_id))
        Animal = c.fetchone()
        Animal = Animal[0]
        NewAnimal = Animal + 1
        c.execute("UPDATE animals SET %s = '%d' WHERE user_id = %d" % (NameofAnimal,NewAnimal, user_id))
        conn.commit()
        UpdateDBMoneyDec(user_id, amount)
        vk_session.method("messages.send", {"user_id": event.user_id,
                                            "message": "Покупка прошла успешно\n\nВсе ваша несобраная продукция была автоматически собрана",
                                            "random_id": 0,
                                            "keyboard": keyboardMenu
                                            })
        return True
    else:
        c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
        OldMoney = c.fetchone()
        OldMoney = OldMoney[0]
        NotEnough = amount-OldMoney
        vk_session.method("messages.send", {"user_id": event.user_id,
                                            "message": "Вам не хватает "+str(NotEnough)+"$",
                                            "random_id": 0,
                                            "keyboard": keyboardAnimalsSell
                                            })
        return  False
    ActKey = False
def AmountofAnimal(user_id, NameofAnimal):
    c.execute("SELECT %s FROM animals WHERE user_id = %d" % (NameofAnimal,user_id))
    Count = c.fetchone()
    Count = Count[0]
    return Count
def ProducedbyTime(user_id, NameofAnimal, TimeRequest):
    amount = AmountofAnimal(user_id, NameofAnimal)
    c.execute("SELECT TimeRequest FROM Time WHERE user_id = %d" % user_id)
    Time = c.fetchone()
    Time = Time[0]
    timePassed = TimeRequest-Time
    Ticks = timePassed//60
    c.execute("SELECT %s FROM produce WHERE user_id = %d" % (NameofAnimal,1))
    prod = c.fetchone()
    prod = prod[0]
    return (int(Ticks)*int(amount)*int(prod/60)+int(amount))
def UpdateTimeRequest(user_id, time):
    c.execute("UPDATE Time SET TimeRequest = '%d' WHERE user_id = %d " % (time, user_id))
    conn.commit()
def UpadateDBMoneyProduce(user_id, donate):
    c.execute("SELECT moneyproduce FROM users WHERE user_id = %d" % user_id)
    Donate = c.fetchone()
    OldDonate = Donate[0]
    NewDonate = OldDonate + donate
    c.execute("UPDATE users SET moneyproduce = '%d' WHERE user_id = %d" %(NewDonate,user_id))
    conn.commit()
def Coin(user_id, amount):
    side = random.randint(1,1000)
    if (side<700):
        vk_session.method("messages.send", {"user_id": event.user_id,
                                            "message": "Вы выиграли: "+str(int(amount)*2),
                                            "random_id": 0,
                                            "keyboard": keyboardBack
                                            })
        UpadateDBMoney(user_id, int(amount)*2)
    else:
        vk_session.method("messages.send", {"user_id": event.user_id,
                                            "message": "Вы проиграли\n\nПопробуй ещё",
                                            "random_id": 0,
                                            "keyboard": keyboardBack
                                            })
        UpdateDBMoneyDec(user_id, int(amount))
def CanAffordMoney(user_id, amount):
    c.execute("SELECT money FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    if result[0] >= int(amount):
        return True
    elif result[0]<int(amount):
        return False
def Nap(user_id, amount, choose):
    mass = ["☕",".☕","..☕"]
    mug = random.choice(mass)
    if (mug == choose):
        if (mug == "☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы выиграли: "+str(int(amount)*3),
                                                "random_id": 0,
                                                "keyboard": keyboardLose1
                                                })
        elif (mug == ".☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы выиграли: "+str(int(amount)*3),
                                                "random_id": 0,
                                                "keyboard": keyboardLose2
                                                })
        elif (mug == "..☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы выиграли: "+str(int(amount)*3),
                                                "random_id": 0,
                                                "keyboard": keyboardLose3
                                                })
        UpadateDBMoney(user_id, int(amount)*3)
    else:
        if (mug == "☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы проиграли\n\nПопробуй ещё",
                                                "random_id": 0,
                                                "keyboard": keyboardWin1
                                                })
        elif (mug == ".☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы проиграли\n\nПопробуй ещё",
                                                "random_id": 0,
                                                "keyboard": keyboardWin2
                                                })
        elif (mug == "..☕"):
            vk_session.method("messages.send", {"user_id": user_id,
                                                "message": "Вы проиграли\n\nПопробуй ещё",
                                                "random_id": 0,
                                                "keyboard": keyboardWin3
                                                })
        UpdateDBMoneyDec(user_id, int(amount))
def CodeDB(user_id):
    c.execute("SELECT code FROM ref WHERE user_id = %d" % user_id)
    Ref = c.fetchone()
    Ref = Ref[0]
    return Ref
def ReferalsDB(user_id):
    c.execute("SELECT Referals FROM ref WHERE user_id = %d" % user_id)
    Ref = c.fetchone()
    Ref = Ref[0]
    return Ref
def UpdateDBCode(user_id,text):
    c.execute("UPDATE ref SET code = '%s' WHERE user_id = %d " % (text, user_id))
    conn.commit()
def UpdateDBCodeAmount(user_id):
    c.execute("SELECT Referals FROM ref WHERE user_id = %d" % user_id)
    Quan = c.fetchone()
    Quan = int(Quan[0])+1
    c.execute("UPDATE ref SET Referals = '%d' WHERE user_id = %d" %(Quan,user_id))
    conn.commit()
def TakeDBUser(code):
    c.execute("SELECT user_id FROM ref WHERE code = %s" % code)
    Quan = c.fetchone()
    Quan = Quan[0]
    return Quan
def CheckDBCode(code):
    c.execute("SELECT * FROM ref WHERE code = %s" % code)
    result = c.fetchone()
    if result is None:
        return False
    else:
        return True
def UpadateDBMoneyDonate(user_id, donate):
    c.execute("SELECT moneydonate FROM users WHERE user_id = %d" % user_id)
    Donate = c.fetchone()
    OldDonate = Donate[0]
    NewDonate = int(OldDonate) + int(donate)
    c.execute("UPDATE users SET moneydonate = '%d' WHERE user_id = %d" %(int(NewDonate),user_id))
    conn.commit()
def CheckDBRealDonate(user_id):
    c.execute("SELECT realdonate FROM users WHERE user_id = %d" % user_id)
    result = c.fetchone()
    result = result[0]
    return result
def UpdateDBRealDonate(user_id, donate):
    c.execute("SELECT realdonate FROM users WHERE user_id = %d" % user_id)
    Donate = c.fetchone()
    OldDonate = Donate[0]
    NewDonate = int(OldDonate) + int(donate)
    c.execute("UPDATE users SET realdonate = '%d' WHERE user_id = %d" %(int(NewDonate),user_id))
    conn.commit()
def Payment(user_id, amount, numbr):
    c.execute("UPDATE donate SET summ = '%d' WHERE user_id = %d " % (amount, user_id))
    c.execute("UPDATE donate SET payment_id = '%d' WHERE user_id = %d " % (numbr, user_id))
    conn.commit()
    code = str("")+str(":")+str(amount)+str("")+str("")+str("")+str(numbr)
    code = hashlib.md5(code.encode())
    url = str(""+str(amount)+"&o="+str(numbr)+"&s="+str(code.hexdigest())+"&lang=ru")
    vk_session.method("messages.send", {"user_id": event.user_id,
                                        "message": "Ссылка на оплату  \n\n"+url,
                                        "random_id": 0
                                        })
def CheckPayment(user_id):
    c.execute("SELECT payment_id FROM donate WHERE user_id = %d" % user_id)
    result = c.fetchone()
    result = result[0]
    code = str("")+str("kku8fl5u")
    code = hashlib.md5(code.encode())
    url = ""+str(code.hexdigest())+"action=check_order_status&order_id="+str(result)
    print(url)
    answ = request.urlopen(""+str(code.hexdigest())+"action=check_order_status&order_id="+str(result))
    text = answ.readline(3)
    print(text)
def QuestStatus(user_id):
    c.execute("SELECT quest FROM quest WHERE user_id = %d" % user_id)
    result = c.fetchone()
    result = result[0]
    return result
def UpdateQuestStatus(user_id, quest):
    c.execute("UPDATE quest SET quest = '%d' WHERE user_id = %d " % (quest, user_id))
    conn.commit()


keyboardFirstTime = {
    "one_time": True,
    "buttons": [
        [{
                "action": {
                    "type": "text",
                    "label": "&#127873;Получить бонус"
                },
                "color": "default"
            }
        ]
    ]
}
keyboardMenu = {
    "one_time": True,
    "buttons": [
        [{
                "action": {
                    "type": "text",
                    "label": "&#127968;Ферма"
                },
                "color": "default"
            },
            {
                "action": {
                    "type": "text",
                    "label": "&#128019;Животные"
                },
                "color": "default"
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "&#128176;Баланс"
                },
                "color": "default"
            },
            {
                "action": {
                    "type": "text",
                    "label": "&#9989;Задания"
                },
                "color": "default"
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "&#127963;Рынок"
                },
                "color": "default"
            },
            {
                "action":{
                    "type" : "text",
                    "label": "Игры"
                }
            }
        ],
        [
            {
                "action": {
                    "type": "text",
                    "label": "&#127873;Бонус"
                },
                "color": "default"
            },
            {
                "action": {
                    "type": "text",
                    "label": "Кейсы"
                },
                "color": "default"
            },
            {
                "action": {
                    "type": "text",
                    "label": "&#9881;Опции"
                },
                "color": "default"
            }
        ]
    ]
}
keyboardBalance = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Пополнить баланс"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label": "Вывод"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]

}
keyboardMarket ={
    "one_time": True,
    "buttons": [
        [{
                "action": {
                    "type": "text",
                    "label": "Обмен продукции на $"
                },
                "color": "default"
            }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Обмен доната на $"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Обмен золотых яиц на $"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardAnimalsSell = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Кролик (100 в час) - 1000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Курица (600 в час) - 5000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Коза (3200 в час) - 25000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Овца (14000 в час) - 100000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Свинья (80000 в час) - 500000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Лошадь (200000 в час) - 1000000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Корова (670000 в час) - 3000000$"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardBack = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardFarm = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Собрать продукцию"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardGames = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Монетка"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label": "Наперстки"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardNap = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "default"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardWin1 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "negative"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "default"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardWin2 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "negative"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "default"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardWin3 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "negative"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardLose1 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "positive"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "default"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardLose2 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "positive"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "default"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardLose3 = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label":"&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":".&#9749;"
            },
            "color": "default"
        },
        {
            "action": {
                "type": "text",
                "label":"..&#9749;"
            },
            "color": "positive"
        },
        ],
        [{
            "action": {
                "type": "text",
                "label": "Сыграть в наперстки ещё раз"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardSettings = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Поменять пригласительный код"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardPay = {
    "one_time": True,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Проверить оплату"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}
keyboardQuest = {
    "one_time": False,
    "buttons": [
        [{
            "action": {
                "type": "text",
                "label": "Получить награду"
            },
            "color": "default"
        }
        ],
        [{
            "action": {
                "type": "text",
                "label": "Главное меню"
            },
            "color": "default"
        }
        ]
    ]
}


keyboardFirstTime = json.dumps(keyboardFirstTime, ensure_ascii=False).encode('UTF-8')
keyboardFirstTime = str(keyboardFirstTime.decode('UTF-8'))
keyboardMenu = json.dumps(keyboardMenu, ensure_ascii=False).encode('UTF-8')
keyboardMenu = str(keyboardMenu.decode('UTF-8'))
keyboardBalance = json.dumps(keyboardBalance, ensure_ascii=False).encode('UTF-8')
keyboardBalance = str(keyboardBalance.decode('UTF-8'))
keyboardMarket = json.dumps(keyboardMarket, ensure_ascii=False).encode('UTF-8')
keyboardMarket = str(keyboardMarket.decode('UTF-8'))
keyboardAnimalsSell = json.dumps(keyboardAnimalsSell, ensure_ascii=False).encode('UTF-8')
keyboardAnimalsSell = str(keyboardAnimalsSell.decode('UTF-8'))
keyboardBack = json.dumps(keyboardBack, ensure_ascii=False).encode('UTF-8')
keyboardBack = str(keyboardBack.decode('UTF-8'))
keyboardFarm = json.dumps(keyboardFarm, ensure_ascii=False).encode('UTF-8')
keyboardFarm = str(keyboardFarm.decode('UTF-8'))
keyboardGames = json.dumps(keyboardGames, ensure_ascii=False).encode('UTF-8')
keyboardGames = str(keyboardGames.decode('UTF-8'))
keyboardNap = json.dumps(keyboardNap, ensure_ascii=False).encode('UTF-8')
keyboardNap = str(keyboardNap.decode('UTF-8'))
keyboardWin1 = json.dumps(keyboardWin1, ensure_ascii=False).encode('UTF-8')
keyboardWin1 = str(keyboardWin1.decode('UTF-8'))
keyboardWin2 = json.dumps(keyboardWin2, ensure_ascii=False).encode('UTF-8')
keyboardWin2 = str(keyboardWin2.decode('UTF-8'))
keyboardWin3 = json.dumps(keyboardWin3, ensure_ascii=False).encode('UTF-8')
keyboardWin3 = str(keyboardWin3.decode('UTF-8'))
keyboardLose1 = json.dumps(keyboardLose1, ensure_ascii=False).encode('UTF-8')
keyboardLose1 = str(keyboardLose1.decode('UTF-8'))
keyboardLose2 = json.dumps(keyboardLose2, ensure_ascii=False).encode('UTF-8')
keyboardLose2 = str(keyboardLose2.decode('UTF-8'))
keyboardLose3 = json.dumps(keyboardLose3, ensure_ascii=False).encode('UTF-8')
keyboardLose3 = str(keyboardLose3.decode('UTF-8'))
keyboardSettings = json.dumps(keyboardSettings, ensure_ascii=False).encode('UTF-8')
keyboardSettings = str(keyboardSettings.decode('UTF-8'))
keyboardPay = json.dumps(keyboardPay, ensure_ascii=False).encode('UTF-8')
keyboardPay = str(keyboardPay.decode('UTF-8'))
keyboardQuest = json.dumps(keyboardQuest, ensure_ascii=False).encode('UTF-8')
keyboardQuest = str(keyboardQuest.decode('UTF-8'))

vk_session = vk_api.VkApi(token="Your token here")
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

ActKey = False
gameNap = False
gameCoin = False
pict = False
mon = 0
RefCode = False
EnterRef = False
payment = False
paymentcheck = False
ActKeyDon = False

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_user and not(event.from_me):
                if CheckDB(event.user_id) != True and (event.text == "Начать" or event.text == "начать"):
                    EnterRef = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Привет, я вижу ты тут первый раз? Нажимай на кнопку или вводи пригласительный код и получи втупительный бонус)",
                                                        "random_id":0,
                                                        "keyboard": keyboardFirstTime
                                                        })
                    ActKey = False
                elif CheckDB(event.user_id) == True and (event.text == "Начать" or event.text == "начать") :
                    EnterRef = False
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Продолжай в том же духе",
                                                        "random_id":0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                elif event.text == "🎁Получить бонус" and CheckDB(event.user_id) == True:
                    EnterRef = False
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Ты уже получал бонус",
                                                        "random_id":0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                elif event.text == "🎁Получить бонус" and CheckDB(event.user_id) != True and EnterRef == True:
                    RegisterDB(event.user_id)
                    EnterRef = False
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Поздравляю, ты получил бонус в 2000$ и 1 кролика",
                                                        "random_id":0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                elif event.text == "🎁Бонус" and CheckDB(event.user_id) == True:
                    if CheckTime(event.user_id, time.time()) >=6000: #Время для бонуса
                        UpdateTime(event.user_id,time.time())
                        UpadateDBMoney(event.user_id,2000)#Сумма бонуса
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Ты получил бонус в 2000$ &#10004;",
                                                        "random_id":0,
                                                        "keyboard": keyboardMenu
                                                        })
                    else:
                        TimeSpent = CheckTime(event.user_id, time.time())
                        TimeSpent = int(TimeSpent)
                        TimeLeft = 86400 -TimeSpent #Менять время для сбора блнуса туть
                        TimeLeftHrs = str(TimeLeft//3600)
                        TimeLeft = TimeLeft-int(int(TimeLeftHrs)*3600)
                        TimeLeftMin = str(TimeLeft//60)
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "&#10071; Вы уже забирали бонус возвращайтесь через:"+TimeLeftHrs+" ч. "+TimeLeftMin+" мин.",
                                                        "random_id":0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                elif event.text == "💰Баланс" and CheckDB(event.user_id) == True:
                    money  =CheckDBMoney(event.user_id)
                    moneydonate = CheckDBMoneyDonate(event.user_id)
                    moneyproduce = CheckDBMoneyProduce(event.user_id)
                    moneyproduce = str(moneyproduce[0])
                    realdonate = CheckDBRealDonate(event.user_id)
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Вас баланс\n\nБаксы: "+str(money)+ "\n\nПродукция: "+str(moneyproduce)+"\n\nДонат: "+str(moneydonate)+"("+str(int(moneydonate)//10)+" руб)\n\nЗолотые яйца: "+str(realdonate),
                                                        "random_id": 0,
                                                        "keyboard": keyboardBalance
                                                        })
                    ActKey = False
                elif event.text == "Главное меню":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Вжух",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                    gameCoin = False
                    pict = False
                    RefCode = False
                    payment = False
                    ActKeyDon = False
                elif event.text == "🏛Рынок":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "100 продукции = 1$\n\n1 донат = 1.25 $\n\n1 золотое яйцо = 100$",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMarket
                                                        })
                    ActKey = False
                elif event.text == "🐓Животные":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Тут вы можете купить животных чтобы добывать продукцию ",
                                                        "random_id": 0,
                                                        "keyboard": keyboardAnimalsSell
                                                        })
                    ActKey = False
                elif event.text == "Кролик (100 в час) - 1000$":
                    CanAfford(event.user_id, 1000,"lvl1")
                elif event.text == "Курица (600 в час) - 5000$":
                    CanAfford(event.user_id, 5000,"lvl2")
                elif event.text == "Коза (3200 в час) - 25000$":
                    CanAfford(event.user_id, 25000,"lvl3")
                elif event.text == "Овца (14000 в час) - 100000$":
                    CanAfford(event.user_id, 100000,"lvl4")
                elif event.text == "Свинья (80000 в час) - 500000$":
                    CanAfford(event.user_id, 500000,"lvl5")
                elif event.text == "Лошадь (200000 в час) - 1000000$":
                    CanAfford(event.user_id, 1000000,"lvl6")
                elif event.text == "Корова (670000 в час) - 3000000$":
                    CanAfford(event.user_id, 3000000,"lvl7")
                elif event.text == "Обмен продукции на $":
                    c.execute("SELECT moneyproduce FROM users WHERE user_id = %d" % event.user_id)
                    result = c.fetchone()
                    money = (result[0]//100)*0.75
                    donate = (result[0]//100)*0.25
                    c.execute("UPDATE users SET moneyproduce = '%d' WHERE user_id = %d" % (0, event.user_id))
                    UpadateDBMoney(event.user_id, money)
                    UpadateDBMoneyDonate(event.user_id, donate)
                    conn.commit()
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Продано: "+str(result[0])+"\n\nПолучено\n" +str(money)+"💰 на баланс для покупок\n"+str(donate)+"💵 на баланс для вывода",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False
                elif event.text == "Обмен доната на $":
                    ActKey = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите сумму доната который хотите обменять",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif event.text == "Обмен золотых яиц на $":
                    ActKeyDon = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите сумму золотых яиц которые хотите обменять",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif event.text == "🏠Ферма":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Кролик\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl1"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl1", time.time()))+
                                                                   "\n\nКурица\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl2"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl2", time.time()))+
                                                                   "\n\nКоза\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl3"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl3", time.time()))+
                                                                   "\n\nОвца\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl4"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl4", time.time()))+
                                                                   "\n\nСвинья\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl5"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl5", time.time()))+
                                                                   "\n\nЛошадь\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl6"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl6", time.time()))+
                                                                   "\n\nКорова\nКоличество: "+str(AmountofAnimal(event.user_id,"lvl7"))+"\nДобыли: "+str(ProducedbyTime(event.user_id, "lvl7", time.time())),
                                                        "random_id": 0,
                                                        "keyboard": keyboardFarm
                                                        })
                elif event.text == "Собрать продукцию":
                    collect = int(ProducedbyTime(event.user_id, "lvl1", time.time())) + int(ProducedbyTime(event.user_id, "lvl2", time.time())) + int(ProducedbyTime(event.user_id, "lvl3", time.time())) + int(ProducedbyTime(event.user_id, "lvl4", time.time())) + int(ProducedbyTime(event.user_id, "lvl5", time.time())) + int(ProducedbyTime(event.user_id, "lvl6", time.time())) + int(ProducedbyTime(event.user_id, "lvl7", time.time()))
                    UpdateTimeRequest(event.user_id, time.time())
                    UpadateDBMoneyProduce(event.user_id,collect)
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Вы собрали: "+ str(collect),
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })
                elif event.text == "Игры":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Выберите игру",
                                                        "random_id": 0,
                                                        "keyboard": keyboardGames
                                                        })
                elif event.text == "Монетка":
                    gameCoin = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите сумму от 10 до 1000",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif gameCoin == True and event.text:
                    try:
                        if int(event.text)>=10 and int(event.text)<=1000:
                            if CanAffordMoney(event.user_id, event.text) == True:
                                Coin(event.user_id, event.text)
                            else:
                                gameCoin = False
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Вам не хватает денег",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardMenu
                                                                    })
                        else:
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вы должны ввести число от 10 до 1000 ",
                                                                "random_id": 0,
                                                                "keyboard": keyboardBack
                                                                })
                    except:
                        gameCoin = False
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Такой команды не существует",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })


                elif event.text == "Наперстки" or event.text == "Сыграть в наперстки ещё раз":
                    gameNap = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите сумму от 10 до 1000",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif event.text == "⚙Опции":
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Ваш пригласительный код: "+ str(CodeDB(event.user_id))+"\n\nКоличество приглашенных рефералов: "+ str(ReferalsDB(event.user_id)),
                                                        "random_id": 0,
                                                        "keyboard": keyboardSettings
                                                        })
                elif event.text == "Поменять пригласительный код":
                    RefCode = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите пригласительный код (от 6 до 10 цифр)",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif event.text and RefCode == True:
                    try:
                        if len(str(event.text))>=6 and len(str(event.text))<=10 and int(event.text)/1 and CheckDBCode(event.text) == False:
                            UpdateDBCode(event.user_id, event.text)
                            RefCode = False
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Поздравляем, вы поменяли свой реферальный код на:"+ str(event.text),
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                        else:
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вы ввели неправильный код (от 6 до 10 цифр или этот код уже существует)",
                                                                "random_id": 0,
                                                                "keyboard": keyboardBack
                                                                })
                    except:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вы ввели неправильный код (от 6 до 10 цифр)",
                                                            "random_id": 0,
                                                            "keyboard": keyboardBack
                                                            })
                elif EnterRef == True and event.text:
                    try:
                        print(CheckDBCode(event.text))
                        if CheckDBCode(event.text) == True:
                            UpdateDBCodeAmount(TakeDBUser(event.text))
                            RegisterDB(event.user_id)
                            EnterRef = False
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Поздравляю, ты получил бонус в 2000$ и 1 кролика",
                                                                "random_id":0,
                                                                "keyboard": keyboardMenu
                                                                })
                        else:
                            RegisterDB(event.user_id)
                            EnterRef = False
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Такого кода нету, но ты получил бонус в 2000$ и 1 кролика от нашего сообщества",
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                    except:
                        EnterRef = True
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Произошла ошибка, попробуйте ещё раз",
                                                            "random_id": 0,
                                                            "keyboard": keyboardFirstTime
                                                            })


                elif gameNap == True and event.text:
                    try:
                        if int(event.text)>=10 and int(event.text)<=1000:
                            if CanAffordMoney(event.user_id, event.text) == True:
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Выбирай",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardNap
                                                                    })
                                mon= int(event.text)
                                pict = True
                                gameNap = False
                            else:
                                gameNap = False
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Вам не хватает денег",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardMenu
                                                                    })
                        else:
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вы должны ввести число от 10 до 1000 ",
                                                                "random_id": 0,
                                                                "keyboard": keyboardBack
                                                                })

                    except:
                        gameNap = False
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Такой команды не существует",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })
                elif pict == True and(event.text == "☕" or event.text == ".☕" or event.text == "..☕"):
                    pict = False
                    Nap(event.user_id, mon, event.text)


                elif ActKey == True and event.text:
                    try:
                        temp = CheckDBMoneyDonate(event.user_id)
                        conn.commit()
                        if int(event.text) <= int(temp):
                            result = CheckDBMoneyDonate(event.user_id)
                            result = result - int(event.text)
                            c.execute("UPDATE users SET moneydonate = '%d' WHERE user_id = %d" % (result, event.user_id))
                            UpadateDBMoney(event.user_id, int(event.text) * 1.25)
                            conn.commit()
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вы обменяли " + str(event.text) + " и получили " + str(int(event.text) * 1.25),
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                            ActKey = False
                        else:
                            temp = int(event.text) - temp
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вам не хватает: " + str(temp),
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                            ActKey = False
                    except:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вы ввели неправильное значение",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMarket
                                                            })
                        ActKey = False
                elif ActKeyDon == True and event.text:
                    try:
                        temp = CheckDBRealDonate(event.user_id)
                        conn.commit()
                        if int(event.text) <= int(temp):
                            result = CheckDBRealDonate(event.user_id)
                            result = result - int(event.text)
                            c.execute("UPDATE users SET realdonate = '%d' WHERE user_id = %d" % (result, event.user_id))
                            UpadateDBMoney(event.user_id, int(event.text) * 100)
                            conn.commit()
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вы обменяли " + str(event.text) + " и получили " + str(int(event.text) * 100),
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                            ActKeyDon = False
                        else:
                            temp = int(event.text) - temp
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Вам не хватает: " + str(temp),
                                                                "random_id": 0,
                                                                "keyboard": keyboardMenu
                                                                })
                            ActKeyDon = False
                    except:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вы ввели неправильное значение",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMarket
                                                            })
                        ActKeyDon = False
                elif event.text == "Вывод":
                    if int(CheckDBMoney(event.user_id))>=100 and int(CheckDBMoneyDonate(event.user_id))>=10 and int(ReferalsDB(event.user_id))>=3:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Для вывода средств пишите админу",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                    elif CheckDBMoney(event.user_id)<100:
                        money = 100-CheckDBMoney(event.user_id)
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вам не хватает:"+ str(money) + "долларов",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                    elif CheckDBMoneyDonate(event.user_id)<10:
                        donate = 10-CheckDBMoneyDonate(event.user_id)
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вам не хватает:" + str(donate) + " золотых яиц",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                    elif CheckDBMoney(event.user_id)<100 and CheckDBMoneyDonate(event.user_id)<10:
                        money = 100-CheckDBMoney(event.user_id)
                        donate = 10-CheckDBMoneyDonate(event.user_id)
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вам не хватает:"+ str(money) + "долларов и " + str(donate) + " золотых яиц",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                    elif ReferalsDB(event.user_id)<3:
                        ref =3-ReferalsDB(event.user_id)
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Вам не хватает:" + str(ref)+" рефералов",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                elif event.text == "Пополнить баланс":
                    payment = True
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Введите сумму(от 10 до 2000 руб)",
                                                        "random_id": 0,
                                                        "keyboard": keyboardBack
                                                        })
                elif payment == True and event.text:
                    try:
                        if(int(event.text)>=10 and int(event.text)<=2000):
                            Payment(event.user_id, int(event.text), random.randint(100000,999999))
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Чтобы проверить свой статус нажмите на кнопку(если оплата прошла но деньги не прийдут, сразу напишите админу)",
                                                                "random_id": 0,
                                                                "keyboard": keyboardPay
                                                                })
                            paymentcheck = True
                            payment = False
                        else:
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Ввеедено неправильное число",
                                                                "random_id": 0,
                                                                "keyboard": keyboardBack
                                                                })
                    except:
                        payment = False
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Ошибка",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })
                elif paymentcheck == True and event.text == "Проверить оплату":
                    CheckPayment(event.user_id)
                elif event.text == "✅Задания":
                    stat = QuestStatus(event.user_id)
                    if stat == 0:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Текущее задание:\nПодписаться на группу\nНаграда: 100💰",
                                                            "random_id": 0,
                                                            "keyboard": keyboardQuest
                                                            })
                    elif stat == 1:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Текущее задание:\nКупить курицу\nНаграда: 200💰",
                                                            "random_id": 0,
                                                            "keyboard": keyboardQuest
                                                            })
                    elif stat == 2:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Текущее задание:\nПригласить 3 человека\nНаграда: 400💰",
                                                            "random_id": 0,
                                                            "keyboard": keyboardQuest
                                                            })
                    else:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Ты уже выполнил все задания, жди новых)",
                                                            "random_id": 0,
                                                            "keyboard": keyboardQuest
                                                            })
                elif event.text == "Получить награду":
                    try:
                        stat = QuestStatus(event.user_id)
                        if stat == 0:
                            member = vk_session.method("groups.isMember",{"group_id": 194469781,
                                                                    "user_id": event.user_id,
                                                                    })
                            print(member)
                            if member == 1:
                                UpadateDBMoney(event.user_id, 100)
                                UpdateQuestStatus(event.user_id, 1)
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Поздравляю, ты выполнил задание\nНаграда: 100💰",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardMenu
                                                                    })
                            elif member == 0:
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Ты еще не подписался на группу",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardQuest
                                                                    })
                        elif stat == 1:
                            c.execute("SELECT lvl2 FROM animals WHERE user_id = %d" % event.user_id)
                            chick = c.fetchone()
                            chick = chick[0]
                            if chick >= 1:
                                UpadateDBMoney(event.user_id, 200)
                                UpdateQuestStatus(event.user_id, 2)
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Поздравляю, ты выполнил задание\nНаграда: 200💰",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardMenu
                                                                    })
                            else:
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Ты еще не купил курицу",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardQuest
                                                                    })
                        elif stat == 2:
                            refs = ReferalsDB(event.user_id)
                            if refs>=3:
                                UpadateDBMoney(event.user_id, 200)
                                UpdateQuestStatus(event.user_id, 3)
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "Поздравляю, ты выполнил задание\nНаграда: 400💰",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardMenu
                                                                    })
                            else:
                                vk_session.method("messages.send", {"user_id": event.user_id,
                                                                    "message": "У тебя только "+str(refs)+" рефералов",
                                                                    "random_id": 0,
                                                                    "keyboard": keyboardQuest
                                                                    })
                        elif stat >=3:
                            vk_session.method("messages.send", {"user_id": event.user_id,
                                                                "message": "Ты уже выполнил все задания",
                                                                "random_id": 0,
                                                                "keyboard": keyboardQuest
                                                                })

                    except:
                        vk_session.method("messages.send", {"user_id": event.user_id,
                                                            "message": "Ошибка",
                                                            "random_id": 0,
                                                            "keyboard": keyboardMenu
                                                            })




                else:
                    vk_session.method("messages.send", {"user_id": event.user_id,
                                                        "message": "Такой команды нету",
                                                        "random_id": 0,
                                                        "keyboard": keyboardMenu
                                                        })
                    ActKey = False


