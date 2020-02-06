# app/models.py
from app import db


class Task(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return '<Task: {}>'.format(self.task)
