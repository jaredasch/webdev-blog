from app import db
from flask_bcrypt import bcrypt

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), index=True, unique=False)
    lname = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(64), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    nickname = db.Column(db.String(64), index=False, unique=False)
    password = db.Column(db.String(128), index=False, unique=False)
    is_admin = db.Column(db.Boolean)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt(10))

    def check_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), self.password.encode('utf-8')) == self.password.encode('utf-8')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.userID)).filter(followers.c.follower_id == self.id).order_by("date desc")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return "<User %s>" % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    date = db.Column(db.DateTime)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.text)
