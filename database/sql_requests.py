NEW_USER = '''
-- Ззапись пользователя в базу данных
INSERT INTO profile 
    (first_name, last_name, email, password)
VALUES 
    ($1, $2, $3, $4) RETURNING id
'''

NEW_CODE = '''
-- запись кода подтверждения
INSERT INTO confirm_code 
    (id_user, code, created_date, exp_date)
VALUES 
    ($1, $2, $3, $4)
'''

EMAIL_CHECK = '''
--проверка эмейла в базе
SELECT email FROM profile WHERE profile.email = $1
'''

CHECK_CODE = '''
--код подтверждения
SELECT cc.code, cc.exp_date, cc.confirmed FROM confirm_code cc WHERE id_user = $1 and confirmed = TRUE and code=$2
'''

UPDATE_STATUS_PROFILE = '''
-- обновление статуса окончания регистрации и запись uid параметра пользователя
    UPDATE profile SET uid=$1, active = TRUE WHERE id = $2
'''

UPDATE_STATUS_CONFIRM = '''
--обновление статуса действия код авторизации
UPDATE confirm_code SET confirmed=FALSE WHERE id_user=$1 and code=$2

'''

CHECK_PASSWORD = '''
-- получение параля пользователя
SELECT id, password, uid, active FROM profile WHERE email = $1
'''

INSERT_PUBLIC_PRIVATE_KEY = '''
--запись публичного ключа пользователя
INSERT INTO user_data_public_keys
    (id_user, public_key, private_key)
VALUES 
    ($1, $2, $3)
'''

GET_PUBLIC_KEY = '''
--получение прубличного ключа пользователя
SELECT keys FROM user_data_public_keys WHERE id_user = $1
'''

CHECK_UID = '''
-- получение параля пользователя
SELECT uid FROM profile WHERE id = $1
'''

CREATE_FOLDER = '''
-- создание папок пользователя
INSERT INTO user_folder 
    (profile_id, folder_name) 
VALUES
    ($1, $2)
'''