from functools import wraps

from flask import url_for
from flask_sqlalchemy import BaseQuery

class PaginatedQuery:
    def __init__(self, query, size, url_id, key, start=1, limit=25):
        self.query = query
        self.size = size
        self.start = start
        self.limit = limit
        self.url_id = url_id
        self.key = key

    def execute(self):
        items = self.query.paginate(self.start, self.limit, False).items
        url_next = url_for(self.url_id, **{'start': self.start + 1, 'limit': self.limit}) \
                    if self.size > (self.start * self.limit) else None
        url_prev = url_for(self.url_id, **{'start': self.start - 1, 'limit': self.limit}) \
                    if ((self.start - 1) * self.limit) > 0 else None

        return {
            self.key: [item.to_dict() for item in items],
            'next': url_next,
            'prev': url_prev
        }