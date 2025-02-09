from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect
from .. import db
from pybo.models import Question, Answer, User, question_voter
from pybo.forms import QuestionForm, AnswerForm
from datetime import datetime
from pybo.views.auth_views import login_required
from sqlalchemy import func


bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route("/list")
def _list():
    """
    질문 목록
    :return:
    """
    page = request.args.get('page', type=int, default=1) # 페이지
    kw = request.args.get('kw', type=str, default='') # 검색어
    so = request.args.get('so', type=str, default='') # 정렬

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    else:  # recent
        question_list = Question.query.order_by(Question.create_date.desc())

    # 검색어 기반 필터링
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(
            Answer.question_id, Answer.content, User.username).join(
                User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User)\
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |
                    Question.content.ilike(search) |
                    User.username.ilike(search) |
                    sub_query.c.content.ilike(search) |
                    sub_query.c.username.ilike(search)
            ) \
            .distinct()

    # 페이징
    question_list = question_list.paginate(page=page, per_page=10)

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
@login_required
def create():
    """
    질문 등록
    :return:
    """
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        print('question create', g.user)
        question = Question(subject=form.subject.data, content=form.content.data,
                            create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('question/question_form.html', form=form)


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))