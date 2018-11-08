if __name__ == '__main__':
    import os

    from homework_server import create_app

    app = create_app(os.environ.get('CONFIG'))
    
    app_context = app.app_context()
    app_context.push()
    from homework_server import db
    from homework_server.models import Administrator
    db.drop_all()
    db.create_all()
    admin_user = Administrator()
    admin_user.name = 'asd'
    admin_user.username = 'asd'
    admin_user.set_password('asd')
    db.session.add(admin_user)
    db.session.commit()
    app_context.pop()

    app.run('localhost', 5000)