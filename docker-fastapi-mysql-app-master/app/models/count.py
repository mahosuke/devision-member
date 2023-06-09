"""
カウント関連の処理をここに書く
"""
from .abstract import AbstractModel

from hashlib import sha256


class CountModel(AbstractModel):
    """
    カウントなどの情報はここに書く
    """

    def __init__(self, config):
        super().__init__(config)

    
    def count_up(self, stock_count, family_id, stock_name):
        """
        カウントアップ処理
        :param family_name: 家族名
        :return:
        """
        
        sql = " UPDATE `stocks` SET stock_count = stock_count - 1 WHERE family_id =%s and stock_name = '%s';"
        return self.execute(sql, stock_count, family_id, stock_name)



    