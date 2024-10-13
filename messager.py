from ontology.interop.System.Runtime import GetTime, CheckWitness, Log, Notify, Serialize, Deserialize
from ontology.interop.System.Storage import Put, Get, GetContext, Delete, GetReadOnlyContext
from ontology.interop.System.Action import RegisterAction

from ontology.builtins import concat, ToScriptHash, verify_signature, SignatureScheme
from ontology.builtins import *

Refund = RegisterAction('refund_test', 'to', 'amount')
CTX = GetContext()

ALL_CHATS = -1
READ_ONLY_TYPE = 1

def Main(operation,args):

    if operation == 'get_sc':
        pk = args[0]
        sign = args[1]
        ms = args[2]
        return get_sc(pk,sign,ms)

    if operation == 'get_read_only_sc':
        return get_read_only_sc()

    if operation == 'get_data':
        key=args[0]
        return get_data(key)

    if operation == 'save_data':
        key=args[0]
        value=args[1]
        return save_data(key, value)

    if operation == 'delete_data':
        key=args[0]
        return delete_data(key)

    if operation == 'create_chat':
        admin_a = args[0]
        ch_type = args[1]
        return create_chat(admin_a,ch_type)

    if operation == 'chat_count':
        return chat_count()
    
    if operation == 'add_member':
        admin_a = args[0]
        member_a = args[1]
        ch_id = args[2]
        return add_member(admin_a,member_a,ch_id)

    if operation == 'my_chat_count':
        member_a = args[0]
        return my_chat_count(member_a)

    if operation == 'my_chats':
        member_a = args[0]
        return my_chats(member_a)

    if operation == 'my_chats_by_type':
        member_a = args[0]
        ch_type = args[1]
        return my_chats_by_type(member_a,ch_type)

    if operation == 'chat_type':
        ch_id = args[0]
        return chat_type(ch_id)

    if operation == 'set_message':
        member_a = args[0]
        ch_id = args[1]
        message = args[2]
        return set_message(member_a,ch_id,message)

    if operation == 'get_messages':
        member_a = args[0]
        ch_id = args[1]
        count = args[2]
        return get_messages(member_a,ch_id, count)

    if operation == 'get_messages_count':
        ch_id = args[0]
        return get_messages_count(ch_id)

    if operation == 'get_all_chat_mambers':
        ch_id = args[0]
        return get_all_chat_mambers(ch_id)

    if operation == 'get_chat_admin':
        member_a = args[0]
        return get_chat_admin(member_a)

    #-------------- News
    
    if operation == 'delete_member':
        admin_a = args[0]
        member_a = args[1]
        ch_id = args[2]
        return delete_member(admin_a,member_a,ch_id)
        
    if operation == 'delete_chat':
        admin_a = args[0]
        ch_id = args[1]
        return delete_chat(admin_a,ch_id)

    if operation == 'get_lst_messages':
        member_a = args[0]
        return get_lst_messages(member_a)

    if operation == 'add_member_by_link':
        member_a = args[0]
        ch_link = args[1]
        return add_member_by_link(member_a,ch_link)

    if operation == 'get_chat_link':
        ch_id = args[0]
        return get_chat_link(ch_id)

    return False

def get_sc(pk, sign, ms):

    #if verify_signature( pk, sign, ms):
    #    return 4
  
    return concat("AUr5QUfeBADq6BMY6Tp5yuMsUNGpsD7nLZ","-string")
    
def get_read_only_sc():
    return GetReadOnlyContext()

def get_data(key):
    sc = GetContext() 
    data = Get(sc,key)
    Notify(data)
    
def save_data(key, value):
    sc = GetContext() 
    Put(sc,key,value)
    
    resList = []
    resList.append(sc)
    resList.append(key)
    resList.append(value)

    Notify("Its right")
    return resList
    
def delete_data(key):
    sc = GetContext() 
    Delete(sc,key)

# ---------------------------------------------
# Создание чата
# Only Chat Admin
def create_chat(admin_a, ch_type):

    # Получаем количество каналов для генерации Номера текущего чата
    chatCount = Get(CTX,"CC")
    ch_id = chatCount + 1

    Put(CTX,"CC", ch_id)
    Put(CTX, ch_id, admin_a)
    #Записываем тип чата
    Put(CTX,concat(ch_id, "CT") , ch_type)

    if READ_ONLY_TYPE == ch_type:
       Put(CTX,concat(admin_a, ch_id) , ch_id)

    Notify(ch_id)

    #-------------- News
    # Добавляем создателя канала как первого участника
    add_member(admin_a, admin_a, ch_id)

    return ch_id

# Чаты где текущий пользователь админ
def get_chat_admin(member_a):

    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)
    
    list_admin = []
    for ch_id in new_list:
        mamber = Get(CTX, ch_id)
        if mamber == member_a :
            list_admin.append(ch_id)
    
    return list_admin


# Количество всех каналов
# Admin
def chat_count():
    return Get(CTX,"CC")

# Метод добавления участника в переписку
# Only Сhat Admin
def add_member(admin_a, member_a, ch_id):
    #Проверяем или админ запросил канал
    сhannelAdmin = Get(CTX, ch_id)

    if admin_a != сhannelAdmin:  
        Notify("Not Admin")
        return False
   
    list_info = SetKeyValue(member_a, ch_id)
    Put(CTX, member_a, list_info)

    # Теперь чату пишем его мемберов
    ch_id_chenged = concat("KV",ch_id)
    list_info_kv = SetKeyValue(ch_id_chenged, member_a)
    Put(CTX, ch_id_chenged, list_info_kv)
    
    # Теперь напишем месседж когда добавляем пользователя
    # user_added = concat("User added.",member_a)
    # set_message(admin_a,ch_id, user_added)

    return True

# Получить всех мемберов по ch_id
def get_all_chat_mambers(ch_id):

    new_list = []
    new_list_info = Get(CTX, concat("KV",ch_id))
    if new_list_info:
        new_list = Deserialize(new_list_info)

    local_ch_type = Get(CTX,concat(ch_id, "CT"))
    if READ_ONLY_TYPE == local_ch_type:
       return len(new_list)

    return new_list



# Количество всех чатов конкретного клиента
# All Read
def my_chat_count(member_a):

    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)

    return len(new_list)


# Метод получения моих каналов
# Only Member
def my_chats(member_a):
    return  my_chats_by_type(member_a, ALL_CHATS)

# Метод получения моих каналов по типу
# Only Member
def my_chats_by_type(member_a, ch_type):
    
    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)

    if ALL_CHATS == ch_type:
        return new_list
    else:
        sort_list = []
        for one_ch in new_list:
            local_ch_type = Get(CTX,concat(one_ch, "CT"))
            if local_ch_type == ch_type:
                sort_list.append(one_ch)
        return sort_list


def chat_type(ch_id):
    return  Get(CTX,concat(ch_id, "CT"))

def get_chat_link(ch_id):
    admin_a = Get(CTX, ch_id)
    return concat(admin_a, ch_id)

# Метод для записи сообщения
# Only Member
def set_message(member_a,ch_id,message):

    # Проверка или имеет пользователь доступ к переписке
    if check_accsess(member_a,ch_id) == False :
        return False

    local_ch_type = Get(CTX,concat(ch_id, "CT"))
    if READ_ONLY_TYPE == local_ch_type:
         #Проверяем или админ запросил канал
        сhannelAdmin = Get(CTX, ch_id)
        if member_a != сhannelAdmin:  
            Notify("Not Admin")
            return False

    # Получаем количество сообщений в текущей переписке
    messageCount = Get(CTX,concat("MC",ch_id))
    ms_id = messageCount + 1

    # Сохраняем количество сообщений
    Put(CTX,concat("MC",ch_id), ms_id)

    Notify(concat(concat(ch_id, ms_id),concat(concat(member_a,'|'),message)))
    # Само сообщение
    Put(CTX,concat(ch_id, ms_id),concat(concat(member_a,'|'),message))

# Метод для получения сообщения
# Only Member
def get_messages(member_a,ch_id, count):

    # Проверка или имеет пользователь доступ к переписке
    if check_accsess(member_a,ch_id) == False :
        return False

    # Получаем количество сообщений в текущей переписке
    messageCount = Get(CTX,concat("MC",ch_id))

    new_list = []
    for x in range(count):

        ms_id = messageCount - x
        if ms_id > 0:
            new_list.append(Get(CTX,concat(ch_id, ms_id)))
    
    return new_list

# Сообщений в текущем канале
# All Read
def get_messages_count(ch_id):
    return Get(CTX,concat("MC",ch_id))



def delete_member(admin_a, member_a, ch_id):

    # CheckWitness admin_a

    if admin_a == member_a:
        # Сам себя удаляю
        # Проверка или имеет пользователь доступ к переписке
        if check_accsess(member_a,ch_id) == False :
            return False
    else:
        # Aдмин удалят мембера
        #Проверяем или админ запросил канал
        сhannelAdmin = Get(CTX, ch_id)
        if admin_a != сhannelAdmin:  
            Notify("Not Admin")
            return False

    list_info = DeleteKeyValue(member_a, ch_id)
    Put(CTX, member_a, list_info)

    # Теперь чату пишем его мемберов
    ch_id_chenged = concat("KV",ch_id)
    list_info_kv = DeleteKeyValue(ch_id_chenged, member_a)
    Put(CTX, ch_id_chenged, list_info_kv)

    # Notify(concat("Deleted: ", ch_id))

# Удаление чата
def delete_chat(admin_a, ch_id):
    # CheckWitness admin_a

    member_list = get_all_chat_mambers(ch_id)

    for member in member_list:
       
        # В чатах мембера удаляем Id чата
        list_info = DeleteKeyValue(member, ch_id)
        Put(CTX, member, list_info)

        # Теперь чату пишем его мемберов
        ch_id_chenged = concat("KV",ch_id)
        list_info_kv = DeleteKeyValue(ch_id_chenged, member)
        Put(CTX, ch_id_chenged, list_info_kv)

    Delete(CTX, ch_id) 
    Notify(concat("Deleted chat: ", ch_id))

# Получить последние сообщения
def get_lst_messages(member_a):

    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)
    
    ret_list = []
    for ch in new_list:
        # Получаем количество сообщений в текущей переписке
        messageCount = Get(CTX,concat("MC",ch))
        
        if messageCount > 0:
            ret_list.append(Get(CTX,concat(ch, messageCount)))
        else:
            ret_list.append(concat(member_a,"|<m:No messages:m>"))

    return ret_list

# NEW --------------------------------
# Метод добавления участника в переписку по ссылке
# Only Сhat Admin
def add_member_by_link(member_a, ch_link):
    
    ch_id = Get(CTX, ch_link)

    if ch_id is None:
        return False

    local_ch_type = Get(CTX,concat(ch_id, "CT"))
    if READ_ONLY_TYPE != local_ch_type:
       return False
   
    list_info = SetKeyValue(member_a, ch_id)
    Put(CTX, member_a, list_info)

    # Теперь чату пишем его мемберов
    ch_id_chenged = concat("KV",ch_id)
    list_info_kv = SetKeyValue(ch_id_chenged, member_a)
    Put(CTX, ch_id_chenged, list_info_kv)
    
    # Теперь напишем месседж когда добавляем пользователя
    # user_added = concat("User added.",member_a)
    # set_message(admin_a,ch_id, user_added)
 
    return True

# Private functions
# ------------------------------------

# Проверка или имеет пользователь доступ к переписке
def check_accsess(member_a,ch_id):
    #Проверяем наличие списка каналов пользователя
    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)

    if ch_id in new_list:
        return True
    
    Notify(concat("Element Dosnt exist: ", ch_id))
    return False

def SetKeyValue(member_a, ch_id):
    #Проверяем наличие списка каналов пользователя
    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)

    if ch_id in new_list:
        Notify(concat("Element exist: ", ch_id))
        return False

    new_list.append(ch_id)
    list_info = Serialize(new_list)

    Notify(new_list)
    return list_info

def DeleteKeyValue(member_a, ch_id):
    #Проверяем наличие списка каналов пользователя
    new_list = []
    new_list_info = Get(CTX, member_a)
    if new_list_info:
        new_list = Deserialize(new_list_info)

    if (ch_id in new_list) == False:
        Notify(concat("Element Not exist: ", ch_id))
        return False
    
    ret_list = []
    for item in new_list:
        if item != ch_id:
            ret_list.append(item)

    list_info = Serialize(ret_list)
    Notify(ret_list)
    return list_info