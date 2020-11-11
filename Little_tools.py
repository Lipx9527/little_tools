# coding=utf-8
import sys
import time
import hmac, base64, struct, hashlib
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QMessageBox, QFrame,
                             QSplitter, QHBoxLayout, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pyperclip


SECRET = {
    '秘钥一:': 'ABCDEFGHIJKLMNOP',
    '秘钥二:': 'ABCDEFGHIJKLMNOQ',
    '秘钥三:': 'ABCDEFGHIJKLMNOR',
}
DEFAULT_GOOGLE_SECRRT = 'ABCDEFGHIJKLMNOP'


class CalGoogleCode():
    """
    计算谷歌验证码（16位谷歌秘钥，生成6位验证码）
    """
    @staticmethod
    def cal_google_code(secret, current_time=int(time.time()) // 30):
        """
        :param secret:   16位谷歌秘钥
        :param current_time:   时间（谷歌验证码是30s更新一次）
        :return:  返回6位谷歌验证码
        """
        # print('current_time: ', current_time)
        key = base64.b32decode(secret)
        msg = struct.pack(">Q", current_time)
        google_code = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(chr(google_code[19])) & 15  # python3时，ord的参数必须为chr类型
        google_code = (struct.unpack(">I", google_code[o:o + 4])[0] & 0x7fffffff) % 1000000
        return '%06d' % google_code  # 不足6位时，在前面补0


class MyGui(QWidget):
    """基础Gui页面"""
    def __init__(self):
        super().__init__()
        self.code_label = {}  # 验证码QLabel是循环生成的，因需要更新颜色和验证码，故先定义一个空字典，用存每个秘钥对应的QLabel对象
        self.update_code()  # 实例化自己建立的定时更新颜色和验证码线程
        self.init_ui()  # 主窗口

    def init_ui(self):
        self.setGeometry(300, 300, 1000, 600)  # 设置主窗口的位置和大小
        self.setWindowTitle('Simple Little tools')  # 设置主窗口的标题
        self.setWindowIcon(QIcon('pics/icon1.gif'))  # 设置主窗口的图标(左上角)

        # 通用样式
        self.setStyleSheet(
            'QMainWindow{background-color: skyblue}'
            'QPushButton{font-weight: bold; background: skyblue; border-radius: 14px;'
            'width: 64px; height: 28px; font-size: 20px; text-align: center;}'
            'QPushButton:hover{background: rgb(50, 150, 255);}'
            'QLabel{font-weight: bold; font-size: 20px; color: orange}'
            'QLineEdit{width: 100px; font: 微软雅黑}'
        )
        self.main_layout()  # 布局函数
        self.show()  # 显示窗口

    def main_layout(self):
        """
        将整个小工具布局放在一个函数中。
        目前整个界面由一个2x3的小区域组成
        每个区域可以布局实现一个或多个小工具。
        """
        hbox = QHBoxLayout()  # 外层大盒子

        top_left = QFrame()  # 上左QFrame
        # top_left = QHBoxLayout()  # 上左QFrame
        top_left.setFrameShape(QFrame.StyledPanel)  # 显示边框
        top_center = QFrame()  # 上中QFrame
        top_center.setFrameShape(QFrame.StyledPanel)
        top_right = QFrame()  # 上右QFrame
        top_right.setFrameShape(QFrame.StyledPanel)
        # 布局管理器QSplitter
        # 可拖动子控件的边界控制子控件的大小， 算是一个动态的布局管理器
        # 在QSplitter对象中各子控件默认是横向布局的，可以使用Qt.Vertical进行垂直布局
        splitter_top = QSplitter(Qt.Horizontal)  # 横向QSplitter
        splitter_top.addWidget(top_left)  # 将QFrame装入QSplitter中
        splitter_top.addWidget(top_center)
        splitter_top.addWidget(top_right)

        bottom_left = QFrame()  # 下左QFrame
        bottom_left.setFrameShape(QFrame.StyledPanel)
        bottom_center = QFrame()  # 下中QFrame
        bottom_center.setFrameShape(QFrame.StyledPanel)
        bottom_right = QFrame()  # 下右QFrame
        bottom_right.setFrameShape(QFrame.StyledPanel)
        splitter_bottom = QSplitter(Qt.Horizontal)  # 横向QSplitter
        splitter_bottom.addWidget(bottom_left)  # 将QFrame装入QSplitter中
        splitter_bottom.addWidget(bottom_center)
        splitter_bottom.addWidget(bottom_right)

        splitter = QSplitter(Qt.Vertical)  # 竖向QSplitter
        splitter.addWidget(splitter_top)  # 将横向的两个QSplitter装在竖向的那个QSplitter中
        splitter.addWidget(splitter_bottom)

        # 谷歌验证码相关
        # gsk(谷歌秘钥) --> google_secret_key、 gc(谷歌验证码) --> google_code
        gsk_title_label = QLabel("谷歌验证码生成器")
        gsk_title_label.setStyleSheet("font:24px; font-weight: bold; color: black")

        # 手动生成字样
        gsk_by_manual_title_label = QLabel("手动生成")  # 手动生成 字体QLabel
        gsk_by_manual_title_label.setStyleSheet('color: green')  # 字样颜色

        gsk_label = QLabel("秘  钥:")  # 秘钥 字体 QLabel
        gsk_input_box = QLineEdit()  # 秘钥输入框
        gsk_input_box.setPlaceholderText("请输入谷歌秘钥")  # 秘钥输入框的提示信息
        gsk_input_box.setMaxLength(16)  # 最大输入位数
        gsk_cal_btn = QPushButton("生成")  # 生成验证码按钮，点击生成

        gc_label = QLabel("验证码:")  # 验证码字体QLabel
        # QLabel不能设置长度，使用空格占位，让它和QLineEdit一样长，排版好看些
        gc_show_label = QLabel("              ")
        gc_show_label.setStyleSheet('color: black; height: 28px; background: skyblue;'
                                    'border-radius: 14px;')  # gc_show_label样式
        gc_show_label.setAlignment(Qt.AlignCenter)  # QLabel文字居中。 text-align: center无效
        gc_copy_btn = QPushButton("复制")  # 复制按钮

        # 点击更新验证码。因为要传入QLabel和QlineEdit，故使用匿名函数，否则会直接调用。
        # 这里也可以不适用匿名函数，而将gsk_input_box和gc_show_label设为类变量，即 self.gc_input_box和
        # self.gc_show_label，这样connect里面直接 self.get_google_code即可（不要加括号）
        gsk_cal_btn.clicked.connect(lambda: self.get_google_code(gsk_input_box, gc_show_label))
        gc_copy_btn.clicked.connect(lambda: self.copy(gc_show_label))

        # 分割手动更新和自动更新区域，让界面友好一些
        dividing_line = QLabel('*' * 28)  # * QLabel
        dividing_line.setStyleSheet('color: green')  # 分割线颜色

        # 自动更新谷歌验证码
        gsk_by_automatic_title_label = QLabel("自动更新")  # 自动更新 字样QLabel
        gsk_by_automatic_title_label.setStyleSheet('color: green')  # 自动更新 字体颜色

        # 使用一个函数来对要自动更新的谷歌验证码进行布局。（因为可能有多个验证码要更新）
        gsk_by_automatic_vbox = self.gsk_by_automatic_layout()  # 返回一个QVBoxLayout()

        gsk_hbox1 = QHBoxLayout()  # 手动更新验证码布局的第一行QHBoxLayout
        gsk_hbox2 = QHBoxLayout()  # 手动更新验证码布局的第二行QHBoxLayout
        gsk_vbox = QVBoxLayout()   # 整个验证码即将会装入一个QVBoxLayout

        # QHBoxLayout或者QVBoxLayout装小部件时使用addWidget()方法
        gsk_hbox1.addWidget(gsk_label)
        gsk_hbox1.addWidget(gsk_input_box)
        gsk_hbox1.addWidget(gsk_cal_btn)
        gsk_hbox2.addWidget(gc_label)
        gsk_hbox2.addWidget(gc_show_label)
        gsk_hbox2.addWidget(gc_copy_btn)

        # QHBoxLayout和QVBoxLayout相互装，需要使用addLayout()方法
        gsk_vbox.addWidget(gsk_title_label)
        gsk_vbox.addWidget(gsk_by_manual_title_label)
        gsk_vbox.addLayout(gsk_hbox1)
        gsk_vbox.addLayout(gsk_hbox2)
        gsk_vbox.addWidget(dividing_line)
        gsk_vbox.addWidget(gsk_by_automatic_title_label)
        gsk_vbox.addLayout(gsk_by_automatic_vbox)
        gsk_vbox.addStretch()  # 拉伸因子，自动占据剩余的空白位置。如果不使用这个，则两个QHBoxLayout会平分QFrame

        # QFrame装QHBoxLayout或者QVBoxLayout，需要使用setLayout()方法
        # 只能装1个，如果装多个，则仅第一个有效果
        # 因此这里先使用一个QVBoxLayout装下多个QHBoxLayout，之后再装入QFrame中
        top_left.setLayout(gsk_vbox)

        # QHBoxLayout或者QVBoxLayout装QSplitter使用addWidget()方法
        hbox.addWidget(splitter)  # 将竖向的QSplitter装入外层大盒子hbox中
        self.setLayout(hbox)  # 主窗口装入外层大盒子hbox。setLayout参数不能是splitter对象，会报错

    def gsk_by_automatic_layout(self):
        """自动布局。这个函数对谷歌验证码进行循环处理，最后返回一个QVBoxLayout()"""
        vbox = QVBoxLayout()
        if SECRET == {}:  # SECRET为空时直接返回空vbox
            return vbox
        for key in SECRET:  # 循环
            vbox.addLayout(self.gsk_by_automatic_single_line_layout(key))  # 将hbox装入vbox
        return vbox

    def gsk_by_automatic_single_line_layout(self, key):
        """验证码单行布局。 名字 验证码展示 复制按钮"""
        hbox = QHBoxLayout()  # 一行为一个QHBoxLayout
        name_label = QLabel(key)  # 名字QLabel
        # 保护机制: 如果计算谷歌验证码失败，则自动填入error!
        try:
            code = CalGoogleCode.cal_google_code(SECRET[key], int(time.time()) // 30)
        except:
            code = 'error!'
        code = '    ' + code + '    '  # 计算秘钥
        code_label = QLabel()  # 验证码展示QLabel
        code_label.setText(code)  # 验证码展示QLabel内容更新
        code_label.setStyleSheet('color: black; height: 28px; background: skyblue;'
                                 'border-radius: 14px;')   # 验证码QLabel样式
        # 将所有的验证码QLabel存在self.code_label中。其中code_label对象为键，对应的秘钥为值
        self.code_label[code_label] = SECRET[key]
        copy_btn = QPushButton('复制')  # 复制按钮
        copy_btn.clicked.connect(lambda: self.copy(code_label))  # 复制按钮对应的槽函数
        hbox.addWidget(name_label)  # hbox装入名字QLabel
        hbox.addWidget(code_label)  # hbox装入验证码展示QLabel
        hbox.addWidget(copy_btn)    # # hbox装入复制按钮
        return hbox  # 返回验证码单行布局的hbox

    def update_code(self):
        """
        实例化自己建立的任务线程类。相当于槽函数
        """
        self.update = UpdateGoogleCode()  # 实例化自己建立的任务线程类  （自动更新验证码和颜色）
        self.update._update.connect(self.code)  # 设置任务线程发射信号时触发的函数
        self.update.start()  # 启动任务线程

    def code(self, color, flag):
        """
        color和flag就是任务线程返回的数据
        color表示此时验证码应该展示的颜色，str
        flag表示是否要更新验证码，int
        """
        for key in self.code_label:  # 循环所有的展示QLabel
            key.setStyleSheet('color: %s; height: 28px; background: skyblue;'
                              'border-radius: 14px;' % color)   # 更新颜色
            if flag == 1:  # flag为1确定要更新验证码
                try:
                    code = CalGoogleCode.cal_google_code(self.code_label[key], int(time.time()) // 30)
                except:
                    code = 'error!'
                code = '    ' + code + '    '  # 计算秘钥
                key.setText(code)
            else:
                pass   # 否则就不更新

    def get_google_code(self, widget1, widget2):
        secret = widget1.text()  # 获取输入的谷歌秘钥
        if secret == '':  # 如果秘钥为空，则填充默认的谷歌秘钥，并计算谷歌验证码
            secret = DEFAULT_GOOGLE_SECRRT
            widget1.setText(secret)
        try:
            code = CalGoogleCode.cal_google_code(secret, int(time.time()) // 30)
        except:
            widget1.clear()  # 错误的谷歌秘钥计算不出验证码，会报错，直接捕获异常，并清除秘钥输入框
            widget2.setText('              ')
            self.info_box('提示', '秘钥有误,验证码生成失败,请重新输入!', 'pics/cry1.png', 1000)
            return  # 返回空即可，但是必须要有，不然界面会卡住并关闭
        code = '    ' + code + '    '  # 前后加空格目的是为了这个QLabel和QlineEdit长度对齐，让界面和谐一些
        widget2.setText(code)    # 显示验证码

    def copy(self, widget):
        """
        复制函数
        """
        code = widget.text().strip()  # 去除了code首尾的空格
        if code == '':
            self.info_box('提示', '哦豁，复制失败了!', 'pics/cry1.png', 1000)  # code复制失败提示
            return
        self.set_text_to_clipboard(code)  # 复制
        if self.get_text_from_clipboard().strip() == code:  # 读出来的粘贴板值等于code，就复制成功了
            self.info_box("复制", "验证码复制成功!", t=1000)  # 复制提示框，1s后自动关闭
        else:
            self.info_box('提示', '哦豁，复制失败了!', 'pics/cry1.png', 1000)  # 复制失败提示

    def set_text_to_clipboard(self, text):
        """写入内容到粘贴板"""
        pyperclip.copy(text)

    def get_text_from_clipboard(self):
        """从粘贴板内读取内容"""
        return pyperclip.paste()

    def info_box(self, title, text, pic_path='pics/smile1.png', t=1000):
        """提示框，t时间内自动关闭"""
        info_box = QMessageBox()
        # 因为没使用这种方式 QMessageBox.information(self, '复制', '复制成功', QMessageBox.Yes) 写弹出框，
        # 则主窗口的样式不能应用在QMessageBox中，因此重新写了弹出框的部分样式
        info_box.setStyleSheet('QPushButton{font-weight: bold; background: skyblue; border-radius: 14px;'
                               'width: 64px; height: 28px; font-size: 20px; text-align: center;}'
                               'QLabel{font-weight: bold; font-size: 20px; color: orange}'
                               )
        info_box.setIconPixmap(QPixmap(pic_path))  # 自定义图片
        info_box.setWindowIcon(QIcon('pics/icon1.gif'))   # 自定义QMessageBox左上角的小图标
        info_box.setWindowTitle(title)  # 标题
        info_box.setText(text)  # 提示文字
        info_box.setStandardButtons(QMessageBox.Ok)  # QMessageBox显示的按钮
        info_box.button(QMessageBox.Ok).animateClick(t)  # t时间后自动关闭(t单位为毫秒)
        info_box.exec_()  # 如果使用.show(),会导致QMessageBox框一闪而逝


class UpdateGoogleCode(QThread):
    """
    自定义的任务线程。用于自动更新验证码和验证码颜色
    验证码： 到下一个30s时候自动更新验证码
    验证码颜色： 还差5s到下一个30s时，将验证码颜色设置为红色；反之验证码为黑色
    """
    _update = pyqtSignal(str, int)  # 发射信号。str为颜色，int表示是否要更新验证码

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            current_sec = time.time()  # 当前时间戳
            while True:
                rest_sec = int(1000 * (30 - time.time() % 30))  # 还差多少毫秒到下一个30s
                if time.time() >= (current_sec // 30 + 1) * 30:  # 如果当前时间大于下一个30s的起始，则需要更新验证码
                    flag = 1  # 此时flag为1
                    if rest_sec <= 5000:
                        color = 'red'  # 到下一个30s的时间小于5000ms时，则颜色为红
                    else:
                        color = 'black'  # 反之颜色为黑
                    self._update.emit(color, flag)
                    break  # 需要更新验证码时，需要跳出里面这个循环，重新更新一下当前时间戳current_sec
                else:
                    flag = 0  # 当前时间不大于下一个30s的起始，则不需要更新验证码
                    if rest_sec <= 5000:
                        color = 'red'
                    else:
                        color = 'black'
                    self._update.emit(color, flag)
                time.sleep(1)  # 1s发射一次信号


if __name__ == '__main__':
    # 创建应用程序和对象。
    # 每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    app = QApplication(sys.argv)
    qt = MyGui()
    # 系统exit()方法确保应用程序干净的退出
    # exec_()方法有下划线。因为执行是一个Python关键词。因此，exec_()代替
    sys.exit(app.exec_())