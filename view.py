#coding:utf-8
import os
from flask import Flask, session, redirect, url_for, request, flash, render_template, Markup, g, jsonify, send_from_directory
from flask.ext.socketio import SocketIO, emit
from model import db_session, Novel, User, Chapter, Comment
from sqlalchemy import and_, or_, func

app = Flask(__name__)
app.secret_key = 'some_secret'


NOVEL_TXT = os.path.join(os.getcwd(), 'uploads//novel_txt')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['NOVEL_TXT'] = NOVEL_TXT
app.config['COVER_PIC'] = os.path.join(os.getcwd(), 'uploads//cover_pic')
app.config['USER_PIC'] = os.path.join(os.getcwd(), 'uploads//user_pic')

socketio = SocketIO(app)


@app.teardown_request
def handle_teardown_request(exception):
    db_session.remove()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        entries = db_session.query(Novel).limit(100)
        return render_template('index.html', entries=entries)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db_session.query(User).filter(User.email == email).first()
        if user:
            if password == user.password:
                session['id'] = user.id
                session['email'] = user.email
                session['nickname'] = user.nickname
                session['head_pic'] = user.headpic
                session['is_admin'] = user.is_admin
                #1成功，2密码错误，3用户名不存在
                session.pop('error', None)
                return redirect(request.headers['referer'])
            else:
                session['error'] = u'密码错误'
                return redirect(request.headers['referer'])
        else:
            session['error'] = u'用户名不存在'
            return redirect(request.headers['referer'])


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('email', None)
    session.pop('nickname', None)
    session.pop('head_pic', None)
    session.pop('is_admin', None)
    return redirect(request.headers['referer'])


@app.route('/search', methods=['GET', 'POST'])
def novel_search():
    if request.method == 'POST':
        search_items = db_session.query(Novel).filter(or_(Novel.name.like('%'+
                                                                          request.form['search'].encode('utf-8')+'%'),
                                                          Novel.author.like('%'+request.form['search'].encode('utf-8')+'%'))).all()

        return render_template('search.html', search_items=search_items)
    elif request.method == 'GET':
        return render_template('search.html', search_items=None)


@app.route('/book/<int:novel_id>', methods=['POST', 'GET'])
def book_infor(novel_id):
    novel = db_session.query(Novel).filter(Novel.id == novel_id).one()
    if request.method == 'GET':
        return render_template('book_infor.html', novel=novel)
    elif request.method == 'POST':
        novel.name = request.form['novel_name']
        novel.author = request.form['novel_author']
        novel.last_update = request.form['novel_last_update']
        novel.type = request.form['novel_type']
        novel.image = request.form['novel_image']
        novel.description = request.form['novel_description']
        novel.recommend = int(request.form['novel_recommend'])
        novel.source_url = request.form['novel_source_url']
        novel.chapter_source_bequge_url = request.form['chapter_source_bequge_url']
        novel.chapter_source_ybd_url = request.form['chapter_source_ybd_url']

        db_session.flush()
        db_session.commit()
        return redirect(request.headers['referer'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/bookmenu/<int:novel_id>', methods=['GET', 'POST'])
def book_menu(novel_id):
    """小说目录"""
    if request.method == 'GET':
        ybd_chapter = db_session.query(Chapter.id, Chapter.name).filter(and_(Chapter.novel_id == novel_id,
                                                                             Chapter.content_source == 1)).all()

        bqg_chapter = db_session.query(Chapter.id, Chapter.name).filter(and_(Chapter.novel_id == novel_id,
                                                                             Chapter.content_source == 2)).all()

        novel = db_session.query(Novel).filter(Novel.id == novel_id).first()

        return render_template('book_menu.html', ybd_chapter=ybd_chapter, novel=novel, novel_id=novel_id,
                               bqg_chapter=bqg_chapter)

    elif request.method == 'POST':
        data = request.get_json()
        novel_text_path = os.path.join(os.getcwd(), 'uploads/novel_txt')
        if data['update_from'] == 1:
            from backtask.getnovelfromybdu import get_single_novel_text
            novel_name, novel_download_url = db_session.query(Novel.name, Novel.chapter_source_ybd_url).\
                filter(Novel.id == novel_id).first()
            get_single_novel_text(novel_download_url.encode('utf-8'), novel_name, str(novel_id), novel_text_path)
            from backtask.getnovel import update_single_chapter_last_and_next, single_from_text_store_sql
            single_from_text_store_sql(novel_text_path, novel_id)
            update_single_chapter_last_and_next(novel_id, 1)
            return jsonify({"good": "1"})
        elif data['update_from'] == 2:
            from backtask.getnovel import update_single_chapter_infor, update_chapter_content
            url = db_session.query(Novel.chapter_source_bequge_url).filter(Novel.id == novel_id).first()[0]
            update_single_chapter_infor(novel_id, url)
            update_chapter_content(novel_id)
            return jsonify({'good': '1'})


def nl2br(s):
    if s is not None:
        result = s.replace('\n', '<br>')
        result = Markup(result)
        return result
    else:
        return

app.jinja_env.filters['nl2br'] = nl2br


@app.route('/read/<int:chapter_id>', methods=['POST', 'GET'])
def book_content(chapter_id):
    """小说章节内容"""
    if request.method == 'GET':
        chapter = db_session.query(Chapter).filter(Chapter.id == chapter_id).first()
        novel_id = chapter.novel_id
        comments = db_session.query(Comment).filter(and_(Comment.from_novel_id == novel_id, Comment.is_host == 1)).order_by(Comment.group_id).all()
        return render_template('book_content.html', chapter=chapter, comments=comments)
    else:
        data = request.get_json()
        chapter_content = data['content'].replace(u'<br>', u'\n')
        chapter = db_session.query(Chapter).filter(Chapter.id == chapter_id).one()
        chapter.content = chapter_content
        db_session.commit()
        return jsonify(code=1)


@app.route('/validate')
def get_validate():
        """生成验证码
        """
        from validate import create_validate_code
        import StringIO
        mstream = StringIO.StringIO()
        img, code = create_validate_code()
        img.save(mstream, "PNG", quality=70)
        session['validate'] = code
        buf_str = mstream.getvalue()
        response = app.make_response(buf_str)
        response.headers['Content-Type'] = 'image/png'
        return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册用户"""
    if request.method == 'GET':
        return render_template('register.html', error_str='')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        nickname = request.form['nickname']
        validate_code = request.form['validate']
        headpic = request.form['head_pic_input']
        user_id = db_session.query(User.id).filter(User.email == email).first()
        nickname_id = db_session.query(User.id).filter(User.nickname == nickname).first()

        if password != repassword:
            return render_template('register.html', error_str=u'密码输入前后不一致')
        elif len(email) < 6 or len(email) > 25:
            return render_template('register.html', error_str=u'用户名在6到25位之间')
        elif user_id:
            return render_template('register.html', error_str=u'用户名已经存在')
        elif nickname_id:
            return render_template('register.html', error_str=u'昵称已经存在')
        elif validate_code != session['validate']:
            return render_template('register.html', error_str=u'验证码错误')
        else:
            new_user = User(email=email, password=password, nickname=nickname, headpic=headpic)
            db_session.add(new_user)
            db_session.commit()
            session['id'] = new_user.id
            session['email'] = new_user.email
            session['nickname'] = new_user.nickname
            session['head_pic'] = new_user.headpic
            session['is_admin'] = new_user.is_admin
            return redirect(request.args['backurl'])


@app.route('/addcomment', methods=['POST', 'GET'])
def comment():
    if request.method == 'POST':
        commentdata = request.get_json()
        post_user_id = int(commentdata['post_user_id'])

        #发表帖子
        if commentdata['is_host']:
            max_group_id = db_session.query(func.max(Comment.group_id)).filter(Comment.from_novel_id == int(commentdata['novel_id'])).first()
            if max_group_id is None:
                group_id = 1
            else:
                group_id = int(max_group_id[0]) + 1

            new_comment = Comment(from_user_id=post_user_id, from_novel_id=int(commentdata["novel_id"]), is_host=True,
                                  group_id=group_id, content=commentdata["comment"])

            db_session.add(new_comment)
            db_session.flush()
            comment_id = new_comment.id
            db_session.commit()
            return jsonify(code=1, comment_id=comment_id, group_id=group_id)

        #回复帖子
        else:
            new_comment = Comment(from_user_id=post_user_id, from_novel_id=int(commentdata['novel_id']), to_user_id=int(commentdata['to_user_id']),
                                  is_host=False, group_id=int(commentdata['group_id']), content=commentdata['comment'])

            db_session.add(new_comment)
            db_session.flush()
            comment_id = new_comment.id
            to_nickname = new_comment.to_user.nickname
            to_headpic = new_comment.to_user.headpic
            db_session.commit()

            return jsonify(code=1, comment_id=comment_id, to_nickname=to_nickname, to_headpic=to_headpic)



#展开评论，得到数据
@app.route('/replycomment', methods=['POST', 'GET'])
def reply_comment():
    if request.method == 'POST':
        replydata = request.get_json()
        group_id = replydata['group_id']

        comments = db_session.query(Comment.id, Comment.from_user.nickname, Comment.from_user.headpic,
                                    Comment.to_user.nickname, Comment.to_user.headpic).filter(and_(Comment.group_id == group_id, Comment.is_host != 1)).all()
        print comments
        return jsonify(comments=comments)



@app.route('/addnovel', methods=['POST', 'GET'])
def add_novel():
    if request.method == 'GET':
        return render_template('addnovel.html')
    elif request.method == 'POST':
        novel_url = request.json['url']
        from backtask.getnovel import update_single_infor
        new_id = update_single_infor(novel_url, add=True)
        return jsonify({'new_id': new_id})


@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')


@socketio.on('my_login')
def handle_connect(data):
    emit('message', {'user': data['user'], 'msg': u'进入房间'}, broadcast=True)


@socketio.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)


@app.route('/cover/<filename>')
def cover_pic(filename):
    return send_from_directory(app.config['COVER_PIC'], filename)


@app.route('/userpic/<filename>')
def user_pic(filename):
    return send_from_directory(app.config['USER_PIC'], filename)


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user(user_id):
    if request.method == 'GET':
        user = db_session.query(User).filter(User.id == user_id).first()
        return render_template('user.html', user=user)
    else:
        return jsonify(code=1)


if __name__ == '__main__':
    #app.debug = True
    #app.debug=True
    #socketio.run(app)
    app.run(debug=True, host='0.0.0.0')
