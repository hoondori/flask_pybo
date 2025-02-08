from flask import Blueprint, render_template, request, url_for
from werkzeug.utils import redirect
from .. import db
from pybo.models import Question, Answer
from pybo.forms import QuestionForm, AnswerForm
from datetime import datetime

bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route("/list")
def _list():
    """
    질문 목록
    :return:
    """
    question_list = Question.query.order_by(Question.create_date.desc())
    return render_template('question/question_list.html', question_list=question_list)

@bp.route("/detail/<int:question_id>")
def detail(question_id):
    """
    질문 상세
    :param question_id: 상세 정보를 보여줄 질문 id
    :return:
    """
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)

@bp.route("/create/", methods=['GET', 'POST'])
def create():
    """
    질문 등록
    :return:
    """

    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data,
                            create_date=datetime.now())
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('question/question_form.html', form=form)