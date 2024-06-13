from PIL import Image, ImageTk
from os import listdir
import os
import random
import tkinter as tk


# 创建拼图块类，包含图块图像和坐标属性
class PuzzlePiece:
    def __init__(self, axis, right_axis, image):
        self.axis = axis
        self.right = right_axis
        self.image = image  # tkinterimage对象

    # 显示拼图块和对应的坐标
    def show(self):
        print("axis:", self.axis, type(self.axis), end=' ')
        print("right: ", self.right, type(self.right))

    # 更改拼图正确坐标
    def change_axis(self, missed_axis):
        self.axis = missed_axis


# 定义拼图类，包含拼图块列表、拼图还原标志、拼图大小等信息
class PuzzleList:
    def __init__(self, pieces, size):
        self.pieces = pieces  # list
        self.flag = False  # 拼图是否还原
        self.piece_size = size  # 拼图块大小
        self.dimension = int(len(pieces) ** 0.5)  # 拼图块维度

    # 重载索引，可根据拼图块现坐标匹配到对应拼图块
    def __getitem__(self, axis):
        for piece in self.pieces:
            if axis == piece.axis:
                return piece

    # 改变两拼图块位置，输入的是拼图块现坐标值
    def exchange_puzzle(self, indexa, indexb):
        # 判断两坐标是否相邻，相邻则允许改变，否则阻止改变
        if (abs(indexa[0] - indexb[0]) == 1 and indexa[1] == indexb[1]) or (
                abs(indexa[1] - indexb[1]) == 1 and indexa[0] == indexb[0]):
            temp = (6, 6)  # 游戏最高维度设置为5，采用（6,6）作临时索引值
            self[indexa].change_axis(temp)
            self[indexb].change_axis(indexa)
            self[temp].change_axis(indexb)
            self.require()  # 每次成功改变坐标后执行还原判断，判定是否成功还原拼图
            return True  # 成功改变坐标
        else:
            return False  # 坐标递送非法，阻止了坐标改变

    # 执行还原成功判断
    def require(self):
        for piece in self.pieces:
            if self[piece.axis].right != piece.axis:
                self.flag = False
                break
        else:
            self.flag = True

    # 在控制台输出拼图相关信息
    def show(self):
        for i in self.pieces:
            i.show()
        print("now: ", self.flag)

    # 打乱拼图块，确保生成有解且随机的题目
    def generate_solvable_puzzle(self):
        seed = random.randint(80, 100)  # 选择一个操作重复数
        blank_index = (self.dimension, self.dimension)  # 定义空拼图块索引值
        for i in range(0, seed):
            # 构建空图块可交换的拼图块列表
            choice_list = [
                (blank_index[0] - 1, blank_index[1]), (blank_index[0], blank_index[1] - 1),
                (blank_index[0] + 1, blank_index[1]), (blank_index[0], blank_index[1] + 1)
            ]
            for j in range(0, len(choice_list)):
                if ((choice_list[j][0] <= 0) or (choice_list[j][1] <= 0)) or (
                        (choice_list[j][0] > self.dimension) or (choice_list[j][1] > self.dimension)):
                    choice_list[j] = None
            while None in choice_list:
                choice_list.remove(None)
            # 随机选择一个可交换的拼图块
            target_index = random.choice(choice_list)
            # 交换拼图
            temp = (6, 6)
            self[target_index].change_axis(temp)
            self[blank_index].change_axis(target_index)
            self[temp].change_axis(blank_index)
            # 更新空拼图块索引值
            blank_index = target_index


# 加载默认图片,返回其文件相对路径
def get_default_image():
    image_files = listdir(r"default_image")
    for i in range(0, len(image_files)):
        image_files[i] = image_files[i]
    return image_files


# 把用户选中的图片处理成拼图块并匹配对应坐标
def format_image(file_path, pieces_num=3):
    former_image = Image.open(file_path)
    # 裁剪非1:1比例的图片
    if former_image.height != former_image.width:
        difference = former_image.height - former_image.width
        if difference > 0:
            box_a = (0, int(abs(difference) / 2))
            box_b = (former_image.width, former_image.width + int(abs(difference) / 2))
            box_c = box_a + box_b
            former_image = former_image.crop(box=box_c)
        else:
            box_a = (int(abs(difference) / 2), 0)
            box_b = (former_image.height + int(abs(difference) / 2), former_image.height)
            box_c = box_a + box_b
            former_image = former_image.crop(box=box_c)
    # 保存原图，以供查看
    former_image.save(r"cache\\original.png", "PNG")
    # 创造拼图块
    pieces_list = []
    for i in range(0, pieces_num):
        for j in range(0, pieces_num):
            unit_x = int(former_image.width / pieces_num)
            unit_y = int(former_image.height / pieces_num)
            box_1 = (i * unit_x, j * unit_y)
            box_2 = ((i + 1) * unit_x, (j + 1) * unit_y)
            box = box_1 + box_2
            piece = former_image.crop(box=box)
            piece = piece.resize((450 // pieces_num, 450 // pieces_num))  # 改变拼图块尺寸
            axis = (i + 1, j + 1)  # 获取拼图块正确坐标
            tpiece = ImageTk.PhotoImage(image=piece)
            pieces_list.append(PuzzlePiece(axis, axis, tpiece))
    # 构建并返回拼图块列表类
    pieces = PuzzleList(pieces_list, 450 // pieces_num)
    # 打乱坐标，生成可接拼图块
    pieces.generate_solvable_puzzle()
    return pieces
