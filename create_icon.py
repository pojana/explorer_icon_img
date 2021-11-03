import pathlib
import os
from natsort import natsorted
import re
import subprocess
import pprint

# 透明画像作成
# convert -size 512x512 xc:none -define png:color-type=2  _basic.png

# 元ファイルを512*512(比率変えないで)に変換
# convert -resize 512x512 '.\2021_01_03_145028, 1345744340648222720, たまには流行りものにのってみよう.jpg' _to.png

# 画像結合し、背景が透明画像のpng作成
# convert .\_basic.png .\_to.png -gravity center  -composite _output.png
# convert H:\_ico\basic.png H:\_ico\Folder.png -gravity southwest -composite _output.png

# アイコン画像作成
# contert '.\2021_01_03_145028, 1345744340648222720, たまには流行りものにのってみよう.jpg' -define icon:auto-resize _humikane.ico


# このプログラム上での流れ
#
# もとのアイコンファイルのサイズを512にする
# convert -resize 512x512 0001_OP.jpg 0001_OP.jpg
#
# 透明画像を背景にして、アイコンファイルを作成
# convert basic.png 0001_OP.jpg -gravity center -composite _output.png
#
# フォルダアイコンを右下に追加
# convert _output.png Folder.png -gravity southwest -composite _output.png
#
# 画像からアイコンを作成
# convert _output.png -define icon:auto-resize _ico.ico

BASIC_IMG = '.\\base\\basic.png'
FOLDER_ICON_IMG = '.\\base\\Folder.png'

dir = ''


class ico():
    def __init__(self):
        pass

    def set_icon(self, set_path, reverse):
        print('\nstart set icon')

        icon_path = self.get_ico_img(set_path, reverse)

        # アイコンパスがあれば、アイコン作成
        if icon_path is None:
            print('no icon_path : {}'.format(set_path))
            pass
        else:
            output_ico_path = self.create_icon(set_path, icon_path)
            self.set_ini(set_path, output_ico_path)
        
        # サブディレクトリにも同じことを
        reverse = False
        sub_dir = self.get_sub_dir(set_path)
        if sub_dir != []:
            for dir in sub_dir:
                set_sub_dir = set_path + dir + '\\'
                self.set_icon(set_sub_dir, reverse)

    def set_ini(self, set_path, icon_path):
        ini_path = set_path + 'desktop.ini'
        icon_path_cull = '.\\' + os.path.basename(icon_path)

        # Desktop.iniを格納するフォルダ自体にR権限を付ける
        att_cmd = 'attrib +R "{}"'.format(set_path[:-1])
        res = subprocess.call(att_cmd)
        # print('att_cmd :{}, res: {}'.format(att_cmd, res))

        # desktop.ini を作成する
        ini_text = '[.ShellClassInfo]\nIconResource={},0'.format(
            icon_path_cull)
        
        pathlib.WindowsPath
        if pathlib.Path.exists(pathlib.WindowsPath(ini_path)):
            os.remove(ini_path)
        else:
            pass
        with open(ini_path, 'w') as ini:
            ini.write(ini_text)

        # desktop.ini を隠しフォルダに設定する
        cmd = 'attrib +h +s "{}"'.format(ini_path)
        print(cmd)
        res = subprocess.call(cmd)

        # _ico.icoを隠しファイルに設定する
        cmd = 'attrib +h +s "{}"'.format(icon_path)
        res = subprocess.call(cmd)

    def create_icon(self, set_path, icon_path):
        temp_ico_path = set_path + '_ico_temp.png'
        output_ico_path = set_path + 'b_ico.ico'
        cmd_list = []

        # もとのアイコンファイルのサイズを512にする
        cmd_list.append('convert -resize 512x512 "{}" "{}"'.format(
            icon_path, temp_ico_path))

        # 透明画像を背景にして、アイコンファイルを作成
        # convert basic.png 0001_OP.jpg -gravity center -composite _output.png
        cmd_list.append('convert "{}" "{}" -gravity center -composite "{}"'.format(
            BASIC_IMG, temp_ico_path, temp_ico_path))

        # フォルダアイコンを右下に追加
        # convert _output.png Folder.png -gravity southwest -composite _output.png
        cmd_list.append('convert "{}" "{}" -gravity southwest -composite "{}"'.format(
            temp_ico_path, FOLDER_ICON_IMG, temp_ico_path))

        # 画像からアイコンを作成
        # convert _output.png -define icon:auto-resize _ico.ico
        cmd_list.append('convert "{}" -define icon:auto-resize "{}"'.format(
            temp_ico_path, output_ico_path))
        if os.path.isfile(output_ico_path):
            os.remove(output_ico_path)
        else:
            pass

        try:
            for i, cmd in enumerate(cmd_list):
                print('cmd No.{} command:{}'.format(i, cmd))
                res = subprocess.call(cmd, shell=True, encoding="utf8")
                if res != 0:
                    print('cmd_process failed :{}'.format(cmd))
                    os.remove(temp_ico_path)
                    return output_ico_path
                else:
                    pass
            os.remove(temp_ico_path)

        except OSError as err:
            # print(err)
            pass
        print('    ->  create icon : {}'.format(output_ico_path))
        return output_ico_path

    def get_sub_dir(self, check_dir):
        files = os.listdir(check_dir)
        files_dir = [f for f in files if os.path.isdir(os.path.join(check_dir, f))]  

        return files_dir

    def get_ico_img(self, check_dir, reverse):

        file_list = list(pathlib.Path(check_dir).glob('*.[jpg][png][gif]'))
        file_list = [os.path.basename(f) for f in file_list]

        file_list = natsorted(file_list, reverse=reverse)
        
        # print(file_list)
        if file_list == []:
            return None
        
        for f in file_list:
            
            if 'ico.jpg' == f:
                icon_file = check_dir + 'ico.jpg'
                return icon_file
            elif 'ico.png' == f:
                icon_file = check_dir + 'ico.png'
                return icon_file
            elif 'ico.gif' == f:
                icon_file = check_dir + 'ico.gif'
                return icon_file
            else:
                pass
        
        icon_file = check_dir + file_list[0]

        # gifはたくさん作られてしまうから
        if '.gif' in icon_file:
            cmd = 'convert -resize 512x512 "{}" "{}"'.format(
                icon_file, check_dir + '_ico_temp.png')
            print(cmd)
            res = subprocess.call(cmd, shell=True, encoding="utf8")
            print('gif convert res:{}'.format(res))

            icon_file = check_dir + 'ico.png'
            # _ico_temp-000.pngがたくさん作られるので,最初だけアイコンに
            
            temp_list = list(pathlib.Path(check_dir).glob('_ico_temp*.png'))

            if len(temp_list) == 1:
                os.rename(check_dir + '_ico_temp.png', icon_file)
            else:
                os.rename(check_dir + '_ico_temp-0.png', icon_file)
                for temp in temp_list:
                    os.remove(temp)

        print('icon_file : {}'.format(icon_file))
        return icon_file


def main():
    icos = ico()

    reverse = True
    # icos.set_icon(dir, reverse)
    # return

    if reverse is True:
        path_list = icos.get_sub_dir(dir)
        path_list = natsorted(path_list)
        # pprint.pprint(path_list)
        path_list = [dir + p + '\\' for p in path_list]

        aleady = 0
        for i, p in enumerate(path_list):
            if i >= aleady:
                icos.set_icon(p, reverse)
            else:
                pass
    else:
        icos.set_icon(dir, reverse)

    
    # icos.set_icon(dir, reverse)

    
if __name__ == '__main__':
    main()
