import os, logging, errno, time, datetime
from importlib import import_module

def standalone_main(cls, *args, **kwargs):
    s = time.time()
    status = 0

    obj = cls(*args, **kwargs)
    obj.parse()

    status = obj.process()
    if status:
        msg = '%s process failed with status: %s' % (cls.__name__, status)
        obj.log.ERROR(msg)
        print(msg)

    obj.close()

    obj.log.info('Time Taken: %s' % datetime.timedelta(seconds=round((time.time()-s))))

def init_logger(filename, level=logging.INFO, frmt=None):
    log = logging.getLogger()
    log.setLevel(level)

    handler = logging.FileHandler(filename)
    log.addHandler(handler)

    frmt = frmt if frmt else '%(asctime)s %(filename)s:%(lineno)s %(levelname)s: %(process)d: %(message)s'
    formatter = logging.Formatter(frmt)
    handler.setFormatter(formatter)

    return log

def close_logger(log):
    logging.shutdown()

def makedir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def import_module_var(path, default):
    module_name, var_name = path.rsplit('.', 1)
    return getattr(import_module(module_name), var_name, default)
