from app import db


class Graphs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    formula = db.Column(db.String(64), nullable=False, index=True)
    period = db.Column(db.String(64), nullable=False)
    step = db.Column(db.String(64), nullable=False)
    image = db.Column(db.String(128))
    status = db.Column(db.String(64))
    updated = db.Column(db.DateTime)
