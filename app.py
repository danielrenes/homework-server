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

    app_context.pop()

    app.run('localhost', 5000)