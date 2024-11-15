import os
import string

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bot.data.config import USER_TABLE_ID, ORDERS_TABLE_ID


class Api:
    def __init__(self):
        self.credentials = None
        if os.path.exists("bot/data/files/token.json"):
            self.credentials = Credentials.from_authorized_user_file(
                "bot/data/files/token.json",
                ['https://www.googleapis.com/auth/spreadsheets']
            )
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "bot/data/files/cred.json",
                    ['https://www.googleapis.com/auth/spreadsheets']
                )
                self.credentials = flow.run_local_server(port=0)

            with open("bot/data/files/token.json", "w") as token:
                token.write(self.credentials.to_json())

    def get_credentials(self):
        return self.credentials

    def get_sheets(self):
        return build("sheets", "v4", credentials=self.get_credentials()).spreadsheets()


class Order:
    @staticmethod
    def get_orders():
        return (Api().get_sheets().values().get(
            spreadsheetId=ORDERS_TABLE_ID,
            range=f'Доставки!A2:K'
        ).execute()).get('values', [])
        
    @staticmethod
    def get_next_order_id():
        try:
            result = Api().get_sheets().values().get(
                spreadsheetId=ORDERS_TABLE_ID,
                range='Доставки!A:A'
            ).execute()
            
            values = result.get('values', [])
            if not values or len(values) <= 1:  # Если таблица пустая или только заголовок
                return 1
                
            # Фильтруем пустые значения и заголовок, конвертируем в числа
            ids = [int(row[0]) for row in values[1:] if row and row[0].isdigit()]
            
            # Если нет ID, начинаем с 1
            if not ids:
                return 1
                
            # Возвращаем следующий ID
            return max(ids) + 1
            
        except Exception as e:
            print(f"Error getting next order id: {e}")
            return 1

    @staticmethod
    def add_order(track_code, status, name, phone, address, user_id):
        result = Api().get_sheets().values().get(
            spreadsheetId=ORDERS_TABLE_ID,
            range=f'Доставки!A:G'
        ).execute()
        values_range = result.get('values', [])
        last_row = len(values_range) + 1
        order_id = Order.get_next_order_id()
        
        range_name = f'Доставки!A{last_row}:G{last_row}'
        return Api().get_sheets().values().batchUpdate(spreadsheetId=ORDERS_TABLE_ID, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": range_name,
                 "majorDimension": "ROWS",
                 "values": [
                     [order_id, track_code, status, name, phone, address, user_id]
                 ]}
            ]
        }).execute()
        
    @staticmethod
    def add_additional_track(track_code):
        result = Api().get_sheets().values().get(
            spreadsheetId=ORDERS_TABLE_ID,
            range=f'Доставки!A:G'
        ).execute()
        values_range = result.get('values', [])
        last_row = len(values_range) + 1
        
        range_name = f'Доставки!A{last_row}:G{last_row}'
        return Api().get_sheets().values().batchUpdate(spreadsheetId=ORDERS_TABLE_ID, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": range_name,
                 "majorDimension": "ROWS",
                 "values": [
                     ["", track_code, "", "", "", ""]
                 ]}
            ]
        }).execute()

class User:

    @staticmethod
    def is_user_auth(user_id):
        try:
            # Получаем все значения
            result = Api().get_sheets().values().get(
                spreadsheetId=USER_TABLE_ID,
                range='Пользователи!A:F'
            ).execute()
            
            values = result.get('values', [])
            if not values:  # Если таблица пустая
                return False
                
            # Пропускаем заголовок (первую строку) и проверяем каждую строку
            for row in values[1:]:
                if row and str(row[0]) == str(user_id):
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Error checking user auth: {e}")
            return False

    @staticmethod
    def user_auth(userid, username, userphione):
        result = Api().get_sheets().values().get(
            spreadsheetId=USER_TABLE_ID,
            range=f'Пользователи!A:F'
        ).execute()
        values_range = result.get('values', [])
        print(len(values_range))

    @staticmethod
    def add_user(user_id, user_name, user_phone, panda_id, promo_code="", status="Обычный"):
        result = Api().get_sheets().values().get(
            spreadsheetId=USER_TABLE_ID,
            range=f'Пользователи!A:F'
        ).execute()
        values_range = result.get('values', [])
        last_row = len(values_range) + 1
        range_name = f'Пользователи!A{last_row}:F{last_row}'
        return Api().get_sheets().values().batchUpdate(spreadsheetId=USER_TABLE_ID, body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": range_name,
                 "majorDimension": "ROWS",
                 "values": [
                     [user_id, user_name, user_phone, panda_id, promo_code, status]
                 ]}
            ]
        }).execute()
        
    @staticmethod
    def clear_user_info(user_id):
        try:
            # Получаем все значения
            result = Api().get_sheets().values().get(
                spreadsheetId=USER_TABLE_ID,
                range='Пользователи!A:F'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return False
            
            # Находим индекс строки
            row_to_update = None
            existing_values = None
            for i, row in enumerate(values):
                if row and str(row[0]) == str(user_id):
                    row_to_update = i + 1  # +1 так как в таблице строки начинаются с 1
                    existing_values = row
                    break
            
            if row_to_update is None:
                return False
            
            # Сохраняем значения первого, четвертого и пятого столбцов (если есть)
            user_id = existing_values[0]
            panda_id = existing_values[3] if len(existing_values) > 3 else ""
            promo_code = existing_values[4] if len(existing_values) > 4 else ""
            
            # Обновляем строку, очищая только второй и третий столбцы
            range_name = f'Пользователи!A{row_to_update}:F{row_to_update}'
            Api().get_sheets().values().update(
                spreadsheetId=USER_TABLE_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={
                    "values": [[user_id, "", "", panda_id, promo_code]]
                }
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error clearing user info: {e}")
            return False
        
        
    @staticmethod
    def update_user_info(user_id, user_name, user_phone):
        try:
            # Получаем все значения
            result = Api().get_sheets().values().get(
                spreadsheetId=USER_TABLE_ID,
                range='Пользователи!A:F'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return False
            
            # Находим индекс строки
            row_to_update = None
            existing_values = None
            for i, row in enumerate(values):
                if row and str(row[0]) == str(user_id):
                    row_to_update = i + 1  # +1 так как в таблице строки начинаются с 1
                    existing_values = row
                    break
            
            if row_to_update is None:
                return False
            
            # Сохраняем значения первого, четвертого и пятого столбцов (если есть)
            panda_id = existing_values[3] if len(existing_values) > 3 else ""
            promo_code = existing_values[4] if len(existing_values) > 4 else ""
            status = existing_values[5] if len(existing_values) > 4 else "Обычный"
            
            # Обновляем только второй и третий столбцы, сохраняя остальные значения
            range_name = f'Пользователи!A{row_to_update}:F{row_to_update}'
            Api().get_sheets().values().update(
                spreadsheetId=USER_TABLE_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={
                    "values": [[user_id, user_name, user_phone, panda_id, promo_code, status]]
                }
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating user info: {e}")
            return False
        
    @staticmethod
    def get_user_data(user_id):
        try:
            # Получаем все значения
            result = Api().get_sheets().values().get(
                spreadsheetId=USER_TABLE_ID,
                range='Пользователи!A:F'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
            
            # Ищем пользователя по ID
            for row in values:
                if row and str(row[0]) == str(user_id):
                    # Создаем словарь с данными пользователя
                    user_data = {
                        'user_id': row[0],
                        'user_name': row[1] if len(row) > 1 else "",
                        'user_phone': row[2] if len(row) > 2 else "",
                        'panda_id': row[3] if len(row) > 3 else "",
                        'promo_code': row[4] if len(row) > 4 else "",
                        'status': row[5] if len(row) > 5 else ""
                    }
                    return user_data
                    
            return None
            
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None
        
    @staticmethod
    def get_next_id():
        try:
            # Получаем все значения
            result = Api().get_sheets().values().get(
                spreadsheetId=USER_TABLE_ID,
                range='Пользователи!D:D'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return 1
                
            # Фильтруем пустые значения и конвертируем в числа
            ids = [int(row[0]) for row in values if row and row[0].isdigit()]
            
            # Если нет ID, начинаем с 1
            if not ids:
                return 1
                
            # Возвращаем следующий ID
            return max(ids) + 1
            
        except Exception as e:
            print(f"Error getting next id: {e}")
            return 1