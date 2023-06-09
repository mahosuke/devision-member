"""
記事モデル
"""
from app.models.abstract import AbstractModel


class StockModel(AbstractModel):
    def __init__(self, config):
        super(StockModel, self).__init__(config)

    def fetche_by_category_id(self, category_id):
        """
        指定されたカテゴリを取得
        :param category_id: 取得したいカテゴリのID
        :return: 指定されたカテゴリのID
        """
        sql = "SELECT * FROM stocks WHERE stocks.category_id=%s"
        return self.fetch_all(sql, category_id)

    def update(self, stock_count, family_id, stock_name):
        """
        カウントアップ処理
        :param family_name: 家族名
        :return:
        """
        
        sql = "UPDATE `stocks` SET stock_count = %s WHERE family_id =%s and stock_name = %s;"
        return self.execute(sql, stock_count, family_id, stock_name)
    
    def fetch_stocks_with_category(self, family_id):
        sql ="SELECT category_name, stock_name, stock_count FROM `stocks` INNER JOIN `categories` ON stocks.category_id = categories.id WHERE stocks.family_id = %s;"
        return self.fetch_all(sql, family_id)

    def create_stocks(self, family_id, category_id, stock_name):
        """
        新しくカテゴリを作成する
        :param cateogry_name: カテゴリの名前
        :return: None
        """
        print('create_stocks')
        sql = "INSERT INTO stocks(stock_name, category_id, stock_count,family_id) VALUE (%s, %s, 0, %s);"
        self.execute(sql, stock_name, category_id, family_id)

    