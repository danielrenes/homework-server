if __name__ == '__main__':
    import os

    from homework_server import create_app

    app = create_app(os.environ.get('CONFIG'))
    
    app_context = app.app_context()
    app_context.push()

    from homework_server import db

    db.drop_all()
    db.create_all()

    from homework_server.models import Administrator

    admin_user = Administrator()
    admin_user.name = 'admin'
    admin_user.username = 'admin'
    admin_user.set_password('admin')
    db.session.add(admin_user)
    db.session.commit()

    from homework_server.models import Teacher
    t = Teacher()
    t.name = 't'
    t.username = 't'
    t.set_password('t')
    db.session.add(t)
    db.session.commit()

    from homework_server.models import Student
    s = Student()
    s.name = 's'
    s.username = 's'
    s.set_password('s')
    db.session.add(s)
    db.session.commit()

    from homework_server.models import Course
    c = Course()
    c.name = 'c'
    c.description = 'c'
    c.teacher_id = t.id
    c.students.append(s)
    db.session.add(c)
    db.session.commit()

    from homework_server.models import Homework
    from datetime import datetime
    h = Homework()
    h.name = 'h'
    h.description = 'h'
    h.deadline = datetime.utcnow()
    h.headcount = 4
    h.self_assignable = False
    h.course_id = c.id
    h.students.append(s)
    db.session.add(h)
    db.session.commit()

    app_context.pop()

    app.run('localhost', 5000)
