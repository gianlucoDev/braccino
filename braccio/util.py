class Singleton(type):
    """
    Metaclass that allows to create singleton classes.

    A singleton class is a class that will get initialized only the first time
    that the constructor is called, every subsequent call to the constructor will
    just reutrn the same instance that was created on the first call.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
