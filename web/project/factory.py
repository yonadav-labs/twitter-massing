from celery import Celery


def create_celery_app(app=None,db=None):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                db.session = db.create_scoped_session()
                try:
                    response = TaskBase.__call__(self, *args, **kwargs)
                finally:
                    db.session.remove()
                return response

    celery.Task = ContextTask
    return celery

