import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import puzzle as pz


# 创建游戏参数设置和文件选择界面
class GetFileWindow:
    def __init__(self, title="游戏设置", size="250x150"):
        self.window = None  # 选择路径主界面 
        self.size = size
        self.title = title
        self.pop_entry_str = None  # 文件路径输入框
        self.next_flag = False  # 判定是否点击了“下一步”以执行游戏界面
        self.choice_window = None  # 选择默认图片界面窗口
        self.choice_box = None  # 创建默认图片列表变量以备用
        self.spin = None  # 游戏维度设置框
        self.dimension = 3  # 游戏维度设置

    # 选择路径界面构造函数
    def construct(self):
        # 构造主窗口界面
        self.window = tk.Tk()
        self.window.title(self.title)
        self.window.geometry(self.size)
        self.window.resizable(False, False)
        # 提示
        label1 = tk.Label(text="请选择图片文件:")
        label1.place(x=0, y=0)
        # 生成文件路径输入框
        self.pop_entry_str = tk.StringVar()
        pop_entry = tk.Entry(self.window, textvariable=self.pop_entry_str)
        pop_entry.place(x=0, y=20, height=25, width=200)
        # 生成路径选择按钮
        pop_choice_button = tk.Button(text="浏览", command=self.get_path)
        pop_choice_button.place(x=205, y=20, height=28)
        # 生成下一步按钮
        pop_next_button = tk.Button(text="下一步", command=self.next)
        pop_next_button.place(x=0, y=100)
        # 生成关闭按钮
        pop_close_button = tk.Button(text="退出", command=self.window.destroy)
        pop_close_button.place(x=140, y=100, width=50)
        # 生成获取默认图片按钮
        pop_default_button = tk.Button(text="选择默认图片", command=self.get_default)
        pop_default_button.place(x=50, y=100)
        # 生成维度设置
        lable2 = tk.Label(text="请设置拼图维度:")
        lable2.place(x=0, y=45)
        self.spin = tk.Spinbox(self.window, from_=3, to=5)
        self.spin.place(x=0, y=65)
        # 运行界面
        self.window.mainloop()
        return self.pop_entry_str.get()

    # 创建获取文件路径函数
    def get_path(self):
        path = filedialog.askopenfilename(title="游戏设置", filetypes=[('图片', '.jpg .png .gif .bmp .jpeg')])
        if path and path.endswith(('.jpg', '.png', '.gif', '.jpeg', '.bmp')):
            self.pop_entry_str.set(path)
        elif path and not path.endswith(('.jpg', '.png', '.gif', '.jpeg', '.bmp')):
            messagebox.showerror(title="错误", message="选择的文件不支持")

    # 创建“下一步”命令函数，改变next_flag值
    def next(self):
        if not self.pop_entry_str.get():
            messagebox.showerror(title="错误", message="选择的拼图题目为空")
        else:
            self.next_flag = True
            self.dimension = self.spin.get()
            self.window.destroy()

    # 创建获取默认图片界面
    def get_default(self):
        # 构建窗口
        self.choice_window = tk.Tk()
        self.choice_window.title("请选择默认图片")
        self.choice_window.geometry("250x100")
        self.choice_window.resizable(False, False)
        # 构建选择列表
        self.choice_box = ttk.Combobox(self.choice_window,state='readonly')
        try:
            file_list = pz.get_default_image()
        except:
            messagebox.showerror(title="错误", message="没有默认图片")
            self.choice_window.destroy()
            return
        if not file_list:
            messagebox.showerror(title="错误", message="没有默认图片")
            self.choice_window.destroy()
            return
        self.choice_box['value'] = file_list
        self.choice_box.current(0)
        self.choice_box.place(x=0, y=20, height=25, width=200)
        # 添加选择按钮
        choice_button = tk.Button(self.choice_window, text="选择", command=self.choice_default)
        choice_button.place(x=0, y=50, width=66)
        # 添加返回按钮
        choice_button = tk.Button(self.choice_window, text="返回", command=self.choice_window.destroy)
        choice_button.place(x=134, y=50, width=66)
        self.choice_window.mainloop()

    # 创建获取选择值的函数
    def choice_default(self):
        self.pop_entry_str.set(r'default_image\\' + self.choice_box.get())
        self.choice_window.destroy()


# 游戏窗口
class GameWindow:
    def __init__(self, image_path, title="拼图游戏", size="600x455", dimension=3):
        self.root_window = None  # 游戏主窗口
        self.title = title
        self.size = size
        self.path = image_path  # 游戏文件路径
        self.dimension = int(dimension)  # 维度
        self.empty_button = None  # 空按钮
        self.empty_index = None  # 空按钮的索引值
        self.puzzle = None  # construct函数内赋值为Pieces_list类对象，存储拼图
        self.button_list = []  # 存储当前按键列表以用于构建拼图
        self.renew = True  # 标志用户是否点击了“切换图片”，游戏是否继续
        self.timer_label = None  # 计时器标签
        self.start_time = None  # 计时开始的时间

    # 更改文件路径和游戏维度
    def set(self, path, dimension):
        self.path = path
        self.dimension = dimension

    # 构造游戏界面
    def construct(self):
        # 处理所选文件
        delete_cache()
        # 构建游戏界面
        self.renew = False
        self.root_window = tk.Tk()
        self.root_window.title(self.title)
        self.root_window.geometry(self.size)
        self.root_window.resizable(False, False)
        # 根据文件路径获取图片生成拼图
        self.puzzle = pz.format_image(self.path, pieces_num=self.dimension)
        self.puzzle.require()
        # 根据拼图初始化拼图按钮布局
        button_size = self.puzzle.piece_size  # 获取拼图块大小
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                index = (i + 1, j + 1)
                # 非空拼图块绑定当前坐标值并以当前坐标值绑定对应命令
                if self.puzzle[index].right != (self.dimension, self.dimension):
                    button = tk.Button(self.root_window, image=self.puzzle[index].image,
                                       command=lambda idx=index: self.change_piece(idx))
                    button.place(x=i * button_size, y=j * button_size, width=button_size, height=button_size)
                    self.button_list.append(button)
                # 移除正确坐标在拼图末尾的拼图，即空拼图块
                else:
                    self.empty_button = tk.Button(self.root_window)
                    self.empty_button.place(x=i * button_size, y=j * button_size, width=button_size, height=button_size)
                    self.empty_index = index
                    self.button_list.append(self.empty_button)
        # 构建查看原图按钮
        show_image_button = tk.Button(self.root_window, text="查看原图", command=self.show_image)
        show_image_button.place(x=480, y=155, width=100, height=50)
        # 构建图片重排按钮
        rerange_button = tk.Button(self.root_window, text="图片重排", command=self.rerange)
        rerange_button.place(x=480, y=230, width=100, height=50)
        # 构建切换图片按钮
        new_photo_button = tk.Button(self.root_window, text="切换图片", command=self.renew_photo)
        new_photo_button.place(x=480, y=305, width=100, height=50)
        # 构建计时器标签
        self.timer_label = tk.Label(self.root_window, text="00:00", font=("Arial", 16))
        self.timer_label.place(x=480, y=80, width=100, height=30)
        self.start_time = time.time()  # 开始计时
        self.update_timer()  # 更新计时器
        self.root_window.mainloop()

    # 更新计时器
    def update_timer(self):
        if not self.puzzle.flag:  # 如果拼图未还原
            current_time = time.time() - self.start_time  # 计算当前时间
            minutes = int(current_time // 60)  # 计算分钟数
            seconds = int(current_time % 60)  # 计算秒数
            time_str = f"{minutes:02d}:{seconds:02d}"  # 格式化时间字符串
            self.timer_label.config(text=time_str)  # 更新计时器标签的文本
            self.root_window.after(1000, self.update_timer)  # 每隔1秒更新一次计时器

    # 重选图片
    def renew_photo(self):
        self.root_window.destroy()
        self.renew = True
        self.root_window = None
        self.empty_button = None
        self.empty_index = None
        self.puzzle = None
        self.button_list = []

    # 图片重排操作
    def rerange(self):
        if self.puzzle.flag:
            return
        for widget in self.root_window.winfo_children():
            if isinstance(widget, tk.Button) and (widget in self.button_list):
                widget.destroy()
        self.button_list = []
        self.empty_button = None
        self.empty_index = None
        self.puzzle.generate_solvable_puzzle()
        self.puzzle.require()
        button_size = self.puzzle.piece_size
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                index = (i + 1, j + 1)
                if self.puzzle[index].right != (self.dimension, self.dimension):
                    button = tk.Button(self.root_window, image=self.puzzle[index].image,
                                       command=lambda idx=index: self.change_piece(idx))
                    button.place(x=i * button_size, y=j * button_size, width=button_size, height=button_size)
                    self.button_list.append(button)
                else:
                    self.empty_button = tk.Button(self.root_window)
                    self.empty_button.place(x=i * button_size, y=j * button_size, width=button_size, height=button_size)
                    self.empty_index = index
                    self.button_list.append(self.empty_button)

    # 查看原图
    def show_image(self):
        full_image_window = tk.Toplevel(self.root_window)
        full_image_window.title("完成图")
        full_image_window.resizable(False, False)
        image = Image.open(r"cache\\original.png")
        image = image.resize((600, 600))
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(full_image_window, image=photo)
        label.image = photo
        label.pack()

    # 用户点击拼图交互核心函数
    def change_piece(self, index):
        # 判断拼图是否还原
        if not self.puzzle.flag:
            # 未还原，尝试更改拼图块
            flag = self.puzzle.exchange_puzzle(index, self.empty_index)
            # 选定拼图块合法，更改成功，更新拼图块绑定指令的index信息和空图块信息
            if flag:
                # 更新屏幕显示拼图块
                x1, y1 = self.empty_button.place_info()['x'], self.empty_button.place_info()['y']
                x2, y2 = self.button_list[(index[0] - 1) * self.dimension + index[1] - 1].place_info()['x'], \
                    self.button_list[(index[0] - 1) * self.dimension + index[1] - 1].place_info()['y']
                self.empty_button.place(x=x2, y=y2)
                self.button_list[(index[0] - 1) * self.dimension + index[1] - 1].place(x=x1, y=y1)
                # 更新button_list数据
                self.button_list[(self.empty_index[0] - 1) * self.dimension + self.empty_index[1] - 1] = \
                    self.button_list[(index[0] - 1) * self.dimension + index[1] - 1]
                self.button_list[(self.empty_index[0] - 1) * self.dimension + self.empty_index[1] - 1].config(
                    command=lambda idx=self.empty_index: self.change_piece(idx))
                self.button_list[(index[0] - 1) * self.dimension + index[1] - 1] = self.empty_button
                self.empty_index = index
        # 拼图已还原，禁用拼图按钮
        if self.puzzle.flag:
            messagebox.showinfo("游戏成功！", "恭喜！你已经成功还原了拼图！")
            for i in self.button_list:
                i.config(state=tk.DISABLED)


# 清空缓存文件夹内的文件
def delete_cache():
    files = os.listdir(r'cache')
    if files:
        for file in files:
            file_path = os.path.join("cache", file)
            os.remove(file_path)


# 程序运行主函数
def main():
    # 生成一个游戏窗口
    main_window = GameWindow(None, dimension=3)
    while main_window.renew:  # 进入非退出循环，用户不结束两个窗口之一则不关闭窗口
        # 创建文件选择界面
        pop_window = GetFileWindow()
        # 获取用户选择的文件路径
        image_path = pop_window.construct()
        # 根据用户在选择窗口选择的路径和设置的游戏维度重设游戏界面
        main_window.set(image_path, int(pop_window.dimension))
        if int(pop_window.dimension)<3 or int(pop_window.dimension) > 5:
            messagebox.showerror(title="错误", message="游戏维度仅能在3-5之间")
            continue
        # 在点击"下一步"的情况下进入游戏界面
        if pop_window.next_flag:
            try:
                main_window.construct()
            except FileNotFoundError:
                messagebox.showerror(title="错误", message="选择的文件不存在")
                continue
        # 否则退出循环程序结束
        else:
            break


# 程序运行入口
if __name__ == "__main__":
    main()
