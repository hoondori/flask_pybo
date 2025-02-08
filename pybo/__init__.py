from flask import Flask
from flask_migrate import Migrate, migrate
from flask_sqlalchemy import SQLAlchemy
import config


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # 설정
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models  # migrate 객체가 models.py를 참조하게 함

    # app에 블루프린트 적용
    from  .views import main_views, question_views, answer_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)





    return app
