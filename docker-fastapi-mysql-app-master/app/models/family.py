"""
家族の名前？関連の処理をここに書く
"""
from .abstract import AbstractModel

from hashlib import sha256


class FamilyModel(AbstractModel):
    """
    ログイン，セッションなどの情報はここに書く
    """

    def __init__(self, config):
        super().__init__(config)

    
    def create_family(self, family_name):
        """
        新規家族作成
        :param family_name: 家族名
        :return:
        """
        
        sql = "INSERT INTO families(family_name) VALUE (%s);"
        self.execute(sql, family_name)


    def find_family_by_family_name(self, family_name):
        """
        家族名から家族を探す
        家族が存在しない場合，空の辞書を返す
        :param family_name: 検索する家族名
        :return: 検索した家族
        """
       
        sql = "SELECT * FROM families where family_name=%s"
        return self.fetch_one(sql, family_name)
    
    def find_families(self):
       
        sql = "select * from families"

        return self.fetch_all(sql)

