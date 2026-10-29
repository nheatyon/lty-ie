from sqlalchemy import Column, Integer, Date, Text, String

from web import WebManager

web = WebManager()


class Redirect(web.model):
    __tablename__ = "redirects"

    MAXIMUM_TAG_LENGTH = 6

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    date_added = Column(Date, nullable=False)
    assigned_tag = Column(String(MAXIMUM_TAG_LENGTH, collation="nocase"), unique=True, nullable=False)
    reference = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Redirect(id={self.id}, date_added={self.date_added}, assigned_tag={self.assigned_tag}, reference={self.reference})>"
