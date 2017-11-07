class BaseClass:
    pass


class SingletonInstance:
    __instance = None

    @classmethod
    def getinstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.getinstance
        return cls.__instance


class MainClass(SingletonInstance):
    def pr(self):
        print(self)
    pass


m1 = MainClass.instance()
m2 = MainClass.instance()

m1.pr()
m2.pr()

print(m1, m2)
