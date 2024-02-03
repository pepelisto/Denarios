


class YourRouter:
    def db_for_read(self, model, **hints):
        if model.__name__.endswith('sim'):
            return 'local'
        return 'local' ###change to default on production, only set local when runing sumulations

    def db_for_write(self, model, **hints):
        if model.__name__.endswith('sim'):
            return 'local'
        return 'local' ###change to default on production, only set local when runing sumulations

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'app' and obj2._meta.app_label == 'app':
            return True
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'app':
            if model_name and model_name.endswith('sim'):
                return db == 'local'
            else:
                return db == 'default' ###change to default on production, only set local when runing sumulations
        return None