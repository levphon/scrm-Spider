import configparser
import os

proDir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(proDir, "config.ini")


# 将整个读取ini的过程封装成一个类

class ReadConfig:
    def __init__(self):
        self.cf = configparser.ConfigParser()  # 调用读取配置模块中的类
        self.cf.read(configPath)  # 读取文件

    def get_ini(self, par, name):
        value = self.cf.get(par, name)  # 通过get方法，读取需要的参数
        return value


r = ReadConfig()  # 实例化
result = r.get_ini("DATABASE", "host")  # 读取DATABASE下的host的值
print(result)
