from cmath import e
from unicodedata import category
from app.models.family import FamilyModel
from app.models.count import CountModel
from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from fastapi.staticfiles import StaticFiles
from app.configs import Config
from app.utilities.session import Session
from app.models.auth import AuthModel
from app.models.articles import ArticleModel
from app.models.categories import CategoryModel
from app.models.stocks import StockModel
from app.utilities.check_login import check_login
from typing import Optional

app = FastAPI()
app.mount("/app/statics", StaticFiles(directory="app/statics"), name="static")
templates = Jinja2Templates(directory="/app/templates")
config = Config()
session = Session(config)


@app.get("/")
def index(request: Request):
    """
    トップページを返す
    :param request: Request object
    :return:
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register")
def register(request: Request):
    """
    新規登録ページ
    :param request:
    :return:
    """
    family_model = FamilyModel(config)
    families = family_model.find_families()

    return templates.TemplateResponse("register.html", {
        "request": request,
        "families": families,
    })

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    ログイン処理
    :param request:
    :param username:
    :param password:
    :return:
    """
    auth_model = AuthModel(config)
    [result, user] = auth_model.login(username, password)
    if not result:
        # ユーザが存在しなければトップページへ戻す
        return templates.TemplateResponse("index.html", {"request": request, "error": "ユーザ名またはパスワードが間違っています"})
    response = RedirectResponse("/categories", status_code=HTTP_302_FOUND)
    # ログインできたらカテゴリ一覧に飛ばす
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.post("/register")
def create_user(username: str = Form(...), password: str = Form(...), family_id: Optional[int] = Form(None), new_family_name: Optional[str] = Form(None)):
    """
    ユーザ登録をおこなう
    フォームから入力を受け取る時は，`username=Form(...)`のように書くことで受け取れる
    :param username: 登録するユーザ名
    :param password: 登録するパスワード
    :return: 登録が完了したら/blogへリダイレクト
    """
    if family_id == None:
        # familyを新規作成してそのidを↓のfamily_idに入れるようにする
        family_model = FamilyModel(config)
        family_model.create_family(new_family_name)
        family = family_model.find_family_by_family_name(new_family_name)
        family_id = family["id"]
    
    auth_model = AuthModel(config)
    auth_model.create_user(username, password, family_id)
    user = auth_model.find_user_by_name_and_password(username, password)
    response = RedirectResponse(url="/categories", status_code=HTTP_302_FOUND)
    session_id = session.set("user", user)
    response.set_cookie("session_id", session_id)
    return response


@app.get("/articles")
# check_loginデコレータをつけるとログインしていないユーザをリダイレクトできる
@check_login
def articles_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    article_model = ArticleModel(config)
    articles = article_model.fetch_recent_articles()
    return templates.TemplateResponse("article-index.html", {
        "request": request,
        "articles": articles,
        "user": user
    })


@app.get("/article/create")
@check_login
def create_article_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-article.html", {"request": request, "user": user})


@app.post("/article/create")
@check_login
def post_article(title: str = Form(...), body: str = Form(...), session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    user_id = session.get(session_id).get("user").get("id")
    article_model.create_article(user_id, title, body)
    return RedirectResponse("/articles", status_code=HTTP_302_FOUND)


@app.get("/article/{article_id}")
@check_login
def article_detail_page(request: Request, article_id: int, session_id=Cookie(default=None)):
    article_model = ArticleModel(config)
    article = article_model.fetch_article_by_id(article_id)
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("article-detail.html", {
        "request": request,
        "article": article,
        "user": user
    })


@app.get("/logout")
@check_login
def logout(session_id=Cookie(default=None)):
    session.destroy(session_id)
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response

@app.get("/categories")
@check_login
def catagories_index(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    category_model = CategoryModel(config)
    categories = category_model.fetch_categories(user['family_id'])
    return templates.TemplateResponse("categories-index.html", {
        "request": request,
        "categories": categories,
        "user": user
    })

@app.get("/category/{category_id}")
@check_login
def category_detail_page(request: Request, category_id: int, session_id=Cookie(default=None)):
    category_model = CategoryModel(config)
    user = session.get(session_id).get("user")
    category = category_model.fetch_categories(user["family_id"])
    stock_model = StockModel(config)
    stocks = stock_model.fetche_by_category_id(category_id=category_id)
  
   
    return templates.TemplateResponse("category-detail.html", {

        "request": request,
        "category_id": category_id,
        "stocks": stocks,
        "user": user,
        
    })

@app.post("/update_stock")
@check_login
def update_stock(stock_count:int = Form(...), stock_name:str = Form(...), category_id: int = Form(...), session_id=Cookie(default=None)):
    family_id = session.get(session_id).get("user").get("family_id")
    stock_model = StockModel(config)
    stock_model.update(stock_count, family_id, stock_name)
    response = RedirectResponse(url="/category/"+str(category_id), status_code=HTTP_302_FOUND)
    return response



@app.get("/category_create")
@check_login
def create_category_page(request: Request, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-categories.html", {"request": request, "user": user})


@app.post("/category_create")
@check_login
def post_category(new_category_name: str = Form(...), session_id=Cookie(default=None)):
    category_model = CategoryModel(config)
    family_id = session.get(session_id).get("user").get("family_id")
    print(f"{new_category_name=}{family_id=}")
    category_model.create_category(family_id, new_category_name)
    return RedirectResponse("/categories", status_code=HTTP_302_FOUND)



@app.get("/stock_create/{category_id}")
@check_login
def create_stock_page(request: Request, category_id: int, session_id=Cookie(default=None)):
    user = session.get(session_id).get("user")
    return templates.TemplateResponse("create-stocks.html", {"request": request, "user": user, "category_id": category_id})


@app.post("/stock_create")
@check_login
def post_stock(new_stock_name: str = Form(...), category_id: int = Form(...), session_id=Cookie(default=None)):
    stock_model = StockModel(config)
    family_id = session.get(session_id).get("user").get("family_id")
    print(f"{new_stock_name=}{family_id=}")
    stock_model.create_stocks(family_id, category_id, new_stock_name)
    return RedirectResponse("/category/{}".format(category_id), status_code=HTTP_302_FOUND)

@app.post("/")
@check_login
def post_category(new_category_name: str = Form(...), session_id=Cookie(default=None)):
    category_model = CategoryModel(config)
    family_id = session.get(session_id).get("user").get("family_id")
    print(f"{new_category_name=}{family_id=}")
    category_model.create_category(family_id, new_category_name)
    return RedirectResponse("/categories", status_code=HTTP_302_FOUND)

@app.get("/order")
@check_login
def order_page(request: Request, session_id=Cookie(default=None)):
    stock_model = StockModel(config)
    family_id = session.get(session_id).get("user").get("family_id")
    stocks = stock_model.fetch_stocks_with_category(family_id)
    category_stocks = {}
    for stock in stocks:
        category_name = stock['category_name']
        stock_name = stock['stock_name']
        stock_count = stock['stock_count']
        if category_name in category_stocks:
            category_stocks[category_name].append(
                {'stock_name': stock_name, 'stock_count': stock_count}
            )
        else:
            category_stocks[category_name] = [{'stock_name': stock_name, 'stock_count': stock_count}]
    user = session.get(session_id).get("user")

    return templates.TemplateResponse("order.html", {"request": request, "user": user, "category_stocks":category_stocks})

