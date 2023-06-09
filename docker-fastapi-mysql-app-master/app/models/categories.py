"""
カテゴリモデル
"""
from app.models.abstract import AbstractModel


class CategoryModel(AbstractModel):
    def __init__(self, config):
        super(CategoryModel, self).__init__(config)

    def fetch_categories(self, family_id):
        """
        カテゴリを取得する．
        :return:
        """
        sql = "SELECT * FROM categories WHERE family_id = %s"
        return self.fetch_all(sql, family_id)

   


    
    def create_category(self, family_id, category_name):
        """
        新しくカテゴリを作成する
        :param cateogry_name: カテゴリの名前
        :return: None
        """
        sql = "INSERT INTO categories(family_id, category_name) VALUE (%s, %s);"
        self.execute(sql, family_id, category_name)

