# OUTLINE

# 1
# open run_data.star and read
# _rlnAngleRot #17 _rlnAngleTilt #18  _rlnAnglePsi #5
# save to a list and save temp
#
# input: run_data.star
# output: euler_angle_list.json
#   a list of tuple(_rlnAngleRot #17,_rlnAngleTilt #18,_rlnAnglePsi #5,_rlnImageName #6)


# 2
# read temp (euler_angle_list.json)
# and show
# number of particles vs angle Rot Tilt Psi
# Rot|tilt|Psi vs number of particles by histogram
# rot vs tilt by heat map
# by matplotlib.pyplot
# determine rot tilt psi manually
# input:euler_angle_list.json
# output:
#   PsiVsParticle.png
#   RotsParticle.png
#   TiltVsParticle.png
#   heatmap_RotVsTilt.png
#   euler_angle_group.json:
#       list(list(A),list(B))
#


# 3
# input :
# rot tilt psi range
# degree(like 20% removed)| number(like 200o p) you want to remove,and origin relion_data.star
# output relion_data_changed.star


# 1

import json
import random
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class RelionStarParser:
    """
# 1
# open run_data.star and read
# _rlnanglerot #17 _rlnangletilt #18  _rlnanglepsi #5
# save to a list and save temp
#
# input: run_data.star
# output: euler_angle_list.json
#   a list of tuple(_rlnanglerot #17,_rlnangletilt #18,_rlnanglepsi #5,_rlnimagename #6)
    """

    def __init__(self, star_file: str, output_dir='./'):
        self.__star_file = star_file
        if output_dir.strip()[-1] == '/':
            self.output_dir = output_dir.strip()
        else:
            self.output_dir = output_dir.strip() + '/'

        self.__parser(self.__star_file)
        self.__print_info()

    def __print_info(self):

        print("\nopening '{}euler_angle_list.json' ...".format(self.output_dir))
        print("\noutput direction is : {} ".format(self.output_dir))
        f_json = open('{}euler_angle_list.json'.format(self.output_dir), 'r')
        euler_list = json.load(f_json)
        print("\nthere is {} particles in '{}'".format(len(euler_list), self.__star_file))
        f_json.close()

        print("\n'{}euler_angle_list.json' is a list of ".format(self.output_dir))
        print("tuple(_rlnanglerot #17,_rlnangletilt #18,_rlnanglepsi #5,_rlnimagename #6)")

    def __parser(self, star_file: str = './run_data_short.star'):

        print("\ninput file is:")
        print(">", self.__star_file)

        record_flag = False
        euler_angle_list = []  # list of tuple(_rlnanglerot #17,_rlnangletilt #18,_rlnanglepsi #5,_rlnimagename #6)

        with open(star_file, 'r') as fin:
            for line in fin:
                line = line.strip()

                if line:
                    # print(line)
                    if line[0] == '#':
                        continue
                    if line[0] != '_' and 'loop_' in line:
                        record_flag = True
                        continue
                    if record_flag and ('_rln' in line):
                        # this is label, include
                        # print(line)
                        pass
                    elif record_flag and not ('_rln' in line):
                        # turn line:str to list
                        line_list = line.split()
                        # all particles is here
                        if len(line_list) == 26:  # data length is 26, change this if you want other data
                            # print _rlnanglerot #17 _rlnangletilt #18  _rlnanglepsi #5  _rlnimagename #6
                            # print(line_list[16], line_list[17], line_list[4], line_list[5])
                            # add to euler_angle_list for saving
                            euler_angle_list.append((line_list[16], line_list[17], line_list[4], line_list[5]))

                else:
                    record_flag = False
        # save euler_angle_list to file as json
        with open('{}euler_angle_list.json'.format(self.output_dir), 'w') as fi_out:
            json.dump(euler_angle_list, fi_out)
            print("\neuler angle list saved into: '{}euler_angle_list.json' ".format(self.output_dir))


# 1 end

# 2
class EulerAngleViewer:
    def __init__(self, euler_json_file: str = './euler_angle_list.json', output_dir='./'):
        self.euler_json_file = euler_json_file
        if output_dir.strip()[-1] == '/':
            self.output_dir = output_dir.strip()
        else:
            self.output_dir = output_dir.strip() + '/'

        with open(self.euler_json_file) as fi:
            self.euler_list = json.load(fi)
        #   a list of tuple(_rlnAngleRot #17,_rlnAngleTilt #18,_rlnAnglePsi #5,_rlnImageName #6)
        rot_list = []
        tilt_list = []
        psi_list = []

        for i in self.euler_list:
            rot_list.append(i[0])
            tilt_list.append(i[1])
            psi_list.append(i[2])

        self.rot_list_pd = pd.Series(np.array(rot_list, dtype=float))
        self.tilt_list_pd = pd.Series(np.array(tilt_list, dtype=float))
        self.psi_list_pd = pd.Series(np.array(psi_list, dtype=float))

        # self.final_data_list
        # list[(int interval_index,
        #     pd.Interval rot_interval,
        #     pd.Interval tilt_interval,
        #     int group_particle_number,
        #     list[np.ndarray[np.int64]] group_particle_indices,
        #     )]
        self.final_data_list = []

        self.run()

    @staticmethod
    def get_particle_number(pd_s: pd.Series) -> (list, list):
        """
        input:pd.series
        output: (group center coordination:list, group particle number:list,width:float)
        """
        sections = pd.cut(pd_s, np.arange(-200, 200, 5.0))
        grouped = pd_s.groupby(sections)

        group_name_list = []
        group_particle_number = []

        for name, index in grouped.indices.items():
            # print(name)
            # print(len(index))

            group_name_list.append(name)
            group_particle_number.append(len(index))

        group_name_center_list = [i.left + i.length / 2 for i in group_name_list]

        if group_name_list:
            width = float(group_name_list[0].length)
        else:
            width = 1.0

        return group_name_center_list, group_particle_number, width

    @staticmethod
    def auto_label(rects, ax, w):
        """
        called by function make_fig_particlenr2euler

        attach a text label above each bar in *rects*, displaying its height.
        """
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x(), height),
                        xytext=(w, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    def make_fig_particle_nr2euler(self, pd_s: pd.Series, x_label: str = '',
                                   y_label: str = 'number of particles',
                                   title='rot vs particles numbers',
                                   save_name='rot',
                                   ):
        """
        need function "auto_lable"

        """

        x, y, w = self.get_particle_number(pd_s)

        fig, ax = plt.subplots()
        rects = ax.bar(x, y, w * 0.8)

        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)
        ax.set_title(title)

        self.auto_label(rects, ax, w)

        fig.tight_layout()
        fig.set_size_inches(26, 10)

        plt.savefig('{}{}.png'.format(self.output_dir, save_name.strip()), format='png', bbox_inches='tight')
        print("\n>> saved to {}".format('{}{}.png'.format(self.output_dir, save_name.strip())))
        # plt.show()

    def make_heat_map(self):
        #

        sections = pd.cut(self.rot_list_pd, np.arange(-200, 200, 5.0))
        grouped_rot = self.rot_list_pd.groupby(sections)  #
        sections = pd.cut(self.tilt_list_pd, np.arange(-200, 200, 5.0))
        grouped_tilt = self.tilt_list_pd.groupby(sections)

        group_name_list = []
        group_particle_number: list[int] = []
        group_particle_indices: list[np.ndarray[np.int64]] = []

        # grouped_rot: 72 groups | value: from -180 to +180 | (pd.Interval, pd.GroupBy)
        # grouped_tilt: 36 groups | value: from 0 to 180
        for name_i, index_i in grouped_rot.indices.items():  # pd.GroupBy.indices : {pd.Interval:List[particle indices]}
            for name_j, index_j in grouped_tilt.indices.items():
                group_name_list.append((name_i, name_j))
                group_particle_number.append(len((set(index_i) & set(index_j))))
                group_particle_indices.append((set(index_i) & set(index_j)))

        group_particle_number = np.array(group_particle_number, dtype=float)
        group_particle_number_matrix = group_particle_number.reshape(72, -1).T
        group_particle_number_matrix = np.flip(group_particle_number_matrix, 0)

        #

        self.final_data_list = []
        for i in range(len(group_name_list)):
            self.final_data_list.append((int(i),  # 0 int interval indices
                                         group_name_list[i][0],  # 1 pd.Interval rot_interval
                                         group_name_list[i][1],  # 2 pd.Interval tilt_interval
                                         int(group_particle_number[i]),  # 3 number of particles in this group
                                         group_particle_indices[i],  # 4 list of particle indices in this group
                                         ))

        #
        group_name_center_list_rot = []
        group_name_center_list_tilt = []

        for rot, _ in grouped_rot.indices.items():
            group_name_center_list_rot.append(rot.left + rot.length / 2)

        for tilt, _ in grouped_tilt.indices.items():
            group_name_center_list_tilt.append(tilt.left + tilt.length / 2)

        #

        fig, ax = plt.subplots()
        im = ax.imshow(group_particle_number_matrix, aspect='auto')

        # make color bar
        cbar = ax.figure.colorbar(im)
        cbar.ax.set_ylabel("nr. particle", rotation=-90, va="bottom")

        # make scalar
        a = list(range(-180, +180, 5))
        b = []
        for i in a:
            if i % 20 == 0:
                i = str(i)
                b.append(i)
            else:
                b.append('')
        x_label = b
        c = list(range(+180, 0, -5))
        d = []
        for i in c:
            if i % 20 == 0:
                i = str(i)
                d.append(i)
            else:
                d.append('')
        y_label = d
        # make scalar end
        ax.set_xticklabels(x_label)
        ax.set_yticklabels(y_label)
        ax.set_xticks(np.arange(len(group_name_center_list_rot)))
        ax.set_yticks(np.arange(len(group_name_center_list_tilt)))
        ax.set_xlabel('angrot')
        ax.set_ylabel('angtilt')
        ax.set_title("angrot vs angtilt")
        fig.tight_layout()
        fig.set_size_inches(10, 10)
        # plt.show()
        plt.savefig('{}heatmap_rotvstilt.png'.format(self.output_dir), format='png', bbox_inches='tight')
        print("\n>> saved to {}".format('{}heatmap_RotvsTilt.png'.format(self.output_dir)))

    def get_final_data_list(self):
        return self.final_data_list

    def run(self):
        self.make_fig_particle_nr2euler(self.rot_list_pd,
                                        x_label='AngleRot',
                                        title='Angle Rot vs Particle number',
                                        save_name='RotVsParticle')
        self.make_fig_particle_nr2euler(self.tilt_list_pd,
                                        x_label='AngleTilt',
                                        title='Angle Tilt vs Particle number',
                                        save_name='TiltVsParticle')
        self.make_fig_particle_nr2euler(self.psi_list_pd,
                                        x_label='AnglePsi',
                                        title='Angle Psi vs Particle number',
                                        save_name='PsiVsParticle')
        self.make_heat_map()

    # 需要调整 matrix 拿到的方法，看看用不用转置
    # done 20210207
    # heat map 加上 sidebar
    # done 20210207


# 2 end


# 3 remove particles and generate new star file
class StarFileBuilder:
    def __init__(self, out_put_dir=''):
        self.rot_min = -200.0
        self.rot_max = +200.0
        self.tilt_min = -1.0
        self.tilt_max = + 200.0
        self.remove_percent = -1.0
        self.select_percent = 0.0
        self.total_particle_number = 0
        self.particle_number_threshold = -1  # bigger than this value is selected else removed

        self.original_star_file = "./run_data.star"
        self.original_star_dir = os.path.dirname(self.original_star_file.strip())

        if out_put_dir:
            if os.path.exists(out_put_dir) and os.path.isdir(out_put_dir):
                pass
            else:
                os.makedirs(out_put_dir)
            self.output_dir = out_put_dir
        else:
            self.output_dir = self.original_star_dir
        self.output_star_file = os.path.join(self.output_dir, 'run_data_removedByMW.star')

        self.final_data_list = []  # should be output of EulerViewer.get_final_data_list()

        self.auto_mode = False

        # intermediate variables
        self.selected_particle_number = 0
        self.selected_particle_indices_list = []  # same format as self.final_data_list
        self.unselected_particle_indices_list = []  # same format as self.final_data_list
        self.particle_indices_list_after_removed = []  # same format as self.final_data_list

    @staticmethod
    def __if_in_interval(pd_interval: pd.Interval, min_value, max_value):
        if max_value - min_value >= 0:
            pass
        else:
            min_value, max_value = max_value, min_value

        if (max_value - min_value) < 1.0 * float(pd_interval.right - pd_interval.left):
            print("Please change input interval and make sure it is bigger than 1*interval_width: {}".format(
                pd_interval.length))
            exit(0)

        if not (min_value > pd_interval.right or
                max_value < pd_interval.left):
            return True
        else:
            return False

    @staticmethod
    def __random_remove_by_percent(i_list, p: float) -> list:
        if i_list and (0.0 < p < 1.0):
            return sorted(random.sample(i_list, int(len(i_list) * (1 - p))))
        else:
            return i_list

    def __remove_particles(self, i_list, p) -> list:
        """
        i_list format as self.final_data_list
        o_list format as self.final_data_list

        call self.__random_remove_by_percent()
        """
        o_list = []
        for i in i_list:
            removed_particle_indices_list = self.__random_remove_by_percent(i[4], p)
            number_remained_particle = len(removed_particle_indices_list)
            o_list.append((i[0], i[1], i[2], number_remained_particle, removed_particle_indices_list))
        return o_list

    @staticmethod
    def __plot_sorted_vs_number_of_particles(i_list, output_dir: str, save_name: str):
        """
        i_list: same format as self.final_data_list
        """

        temp_list = sorted(i_list, key=lambda i: i[3], reverse=True)

        y_list = [i[3] for i in temp_list]
        x_list = range(len(y_list))

        w = 1
        fig, ax = plt.subplots()
        ax.bar(x_list, y_list, w * 0.8)

        ax.set_ylabel('number of particles')
        # ax.set_xlabel(x_label)
        # ax.set_title(title)

        fig.tight_layout()
        fig.set_size_inches(26, 10)

        plt.savefig('{}.png'.format(os.path.join(output_dir.strip(), save_name.strip())), format='png',
                    bbox_inches='tight')
        print("\n>> saved to {}".format('{}.png'.format(os.path.join(output_dir.strip(), save_name.strip()))))

    def __data_parser_normal_mode(self):
        """
        call self.__remove_particles()

        ./normal_mode_sorted_NrParticles_before_removal.png
        will be saved to show the sorted intervals by Number of Particles before removal

        ./normal_mode_sorted_NrParticles_after_removal.png
        will be saved to show the sorted intervals by Number of Particles before removal
        """

        self.total_particle_number = 0
        self.selected_particle_number = 0
        self.selected_particle_indices_list = []  # same format as self.final_data_list
        self.unselected_particle_indices_list = []  # same format as self.final_data_list

        # plot
        self.__plot_sorted_vs_number_of_particles(self.final_data_list,
                                                  self.output_dir,
                                                  'normal_mode_sorted_NrParticles_before_removal')
        # plot end

        # select particles for removal

        if self.final_data_list:
            for i in self.final_data_list:
                self.total_particle_number += i[3]
                if (self.__if_in_interval(i[1], self.rot_min, self.rot_max) and
                        self.__if_in_interval(i[2], self.tilt_min, self.tilt_max) and
                        i[3] >= self.particle_number_threshold):
                    self.selected_particle_number += i[3]
                    self.selected_particle_indices_list.append(i)
                else:
                    self.unselected_particle_indices_list.append(i)
            print('''\n 
                    total {} particles found.\n
                    {} particles selected for next step of removal.\n
                    {} particles kept.'''.format(self.total_particle_number,
                                                 self.selected_particle_number,
                                                 self.total_particle_number - self.selected_particle_number,
                                                 ))

        else:
            print("Please check final_data_list again, it is empty now")

        # select particles for removal end

        # remove x percent particles for each intervals in selected intervals list
        removed_particle_list = self.__remove_particles(self.selected_particle_indices_list, self.remove_percent)
        self.particle_indices_list_after_removed = self.unselected_particle_indices_list + removed_particle_list
        # remove x percent particles for each intervals in selected intervals list end

        # plot
        self.__plot_sorted_vs_number_of_particles(self.particle_indices_list_after_removed,
                                                  self.output_dir,
                                                  'normal_mode_sorted_NrParticles_after_removal')
        # plot end

    def __data_parser_auto_mode(self):
        """
        In auto mode:

        all interval(rot,tilt) groups will be sorted by the number of particles ( rank from most to least).

        When the sum of the number of particels in intervals from the sorted list in descend order

        reach x percent particles of total, those intervals will remove y percent particles for each intervals.


        ./auto_mode_sorted_NrParticles_before_removal.png
        will be saved to show the sorted intervals by Number of Particles before removal

        ./auto_mode_sorted_NrParticles_after_removal.png
        will be saved to show the sorted intervals by Number of Particles before removal


        """
        # plot
        self.__plot_sorted_vs_number_of_particles(self.final_data_list,
                                                  self.output_dir,
                                                  'auto_mode_sorted_NrParticles_before_removal')
        # plot end

        #
        self.total_particle_number = 0

        if self.final_data_list:
            for i in self.final_data_list:
                self.total_particle_number += i[3]

        self.selected_particle_number = 0
        self.selected_particle_indices_list = []  # same format as self.final_data_list
        self.unselected_particle_indices_list = []  # same format as self.final_data_list
        #

        # select

        sorted_list = sorted(self.final_data_list, key=lambda data: data[3], reverse=True)

        temp_sum = 0
        goal_sum = int(self.select_percent * self.total_particle_number)

        for i in sorted_list:
            if temp_sum < goal_sum:
                temp_sum += i[3]
                self.selected_particle_indices_list.append(i)
            else:
                self.unselected_particle_indices_list.append(i)
        print('''\n 
                            total {} particles found.\n
                            {} particles should be selected by select percent {}.\n
                            {} particles selected for next step of removal.\n
                            {} particles kept.'''.format(self.total_particle_number,
                                                         goal_sum,
                                                         self.select_percent,
                                                         temp_sum,
                                                         self.total_particle_number - temp_sum,
                                                         ))
        # select end

        # remove from select
        removed_particle_list = self.__remove_particles(self.selected_particle_indices_list, self.remove_percent)
        self.particle_indices_list_after_removed = self.unselected_particle_indices_list + removed_particle_list

        # remove from select end

        # plot
        self.__plot_sorted_vs_number_of_particles(self.particle_indices_list_after_removed,
                                                  self.output_dir,
                                                  'auto_mode_sorted_NrParticles_after_removal')
        # plot end

    def __data_parser(self):
        if self.auto_mode:
            self.__data_parser_auto_mode()
        elif not self.auto_mode:
            self.__data_parser_normal_mode()

    # end 20210214
    # output : self.particle_indices_list_after_removed # same format as self.final_data_list

    def __save_processed_star_file(self):
        particle_indices_list_temp = [list(i[4]) for i in self.particle_indices_list_after_removed]
        list_temp = []
        for i in particle_indices_list_temp:
            list_temp += i
        particle_indices_list_temp = sorted(list_temp)

        data_index = 0
        with open(self.original_star_file, 'r') as in_file:
            with open(self.output_star_file, 'w') as out_file:
                for line in in_file:
                    if line:
                        if len(line.split()) == 26:
                            if particle_indices_list_temp:
                                if data_index == particle_indices_list_temp[0]:
                                    out_file.write(line)
                                    data_index += 1
                                    particle_indices_list_temp.pop(0)
                                elif data_index != particle_indices_list_temp[0]:
                                    data_index += 1
                            else:
                                break
                        else:
                            out_file.write(line)
                    else:
                        out_file.write('\n')
        print("\n saved to new star file : {}".format(self.output_star_file))

    def __preview_processed_star_file(self):
        pass

    def __print_brief_report(self):
        kept_number = sum([int(i[3]) for i in self.particle_indices_list_after_removed])
        print('''\n 
                    total {} particles found.\n
                    {} particles kept.\n
                    {} particles removed.'''.format(self.total_particle_number,
                                                    kept_number,
                                                    self.total_particle_number - kept_number,
                                                    ))

    def run(self):
        self.__data_parser()
        self.__save_processed_star_file()
        self.__preview_processed_star_file()
        self.__print_brief_report()
        return self.output_star_file


# 3 remove particles and generate new star file end

# 4 integrate
"""
    step 001

    input:
    output_dir = ''  # 总的输出文件夹
    star_file = ''   # 原始star文件
    #  save star_file dir as output_dir 
    output：
    json_file_name = 'euler_angle_list.json'
    json_file = os.path.join(output_dir, json_file_name)

    step 002

    input:
    json_file

    output:
    png files

    temp_file is needed to save final data list

    step 003

    input:
    temp_file
    star_file

    output:
    png files
    new star file

    step 004

    input:
    new star file

    repeat step 001 002

    output:
    png files 


    """


# step 001
def parse_and_preview(star_file='./data/run_data.star'):
    """

    :param star_file:
    :return: euler_viewer.get_final_data_list(), output_dir

    will build two output dir by input star file's dirname:
       001_star_parse
       002_euler_viewer
    """

    output_dir = './'
    if os.path.exists(star_file) and os.path.isfile(star_file):
        output_dir = os.path.dirname(star_file)
        if not os.path.exists(os.path.join(output_dir, 'fix_Euler_output')):
            os.makedirs(os.path.join(output_dir, 'fix_Euler_output'))
        output_dir = os.path.join(output_dir, 'fix_Euler_output')
    else:
        print("Please recheck you input star file. Does it exist ?")
        exit(0)

    if not os.path.exists(os.path.join(output_dir, '001_star_parse')):
        os.makedirs(os.path.join(output_dir, '001_star_parse'))

    step001_out_dir = os.path.join(output_dir, '001_star_parse')

    star_parser = RelionStarParser(star_file, output_dir=step001_out_dir)

    # step 001 end

    # step 002
    json_file = os.path.join(step001_out_dir, 'euler_angle_list.json')
    if not os.path.exists(os.path.join(output_dir, '002_euler_viewer')):
        os.makedirs(os.path.join(output_dir, '002_euler_viewer'))

    step002_out_dir = os.path.join(output_dir, '002_euler_viewer')

    euler_viewer = EulerAngleViewer(json_file, output_dir=step002_out_dir)

    return euler_viewer.get_final_data_list(), output_dir

    # step 002 end

    # step003


def fix_euler_distribution(
        star_file='./data/run_data.star',
        output_dir='./',
        final_data_list: list = [],
        rot_min=-200.0,
        rot_max=+200.0,
        tilt_min=-1.0,
        tilt_max=+ 200.0,
        remove_percent=0.3,
        select_percent=0.2,  # when auto_mode=False,this value will be ignored
        particle_number_threshold=-1,  # bigger than this value is selected else removed
        auto_mode=False,
):
    if not os.path.exists(os.path.join(output_dir, '003_fix_euler')):
        os.makedirs(os.path.join(output_dir, '003_fix_euler'))
    step003_out_dir = os.path.join(output_dir, '003_fix_euler')
    remover = StarFileBuilder(out_put_dir=step003_out_dir)
    remover.original_star_file = star_file
    remover.final_data_list = final_data_list
    remover.auto_mode = auto_mode
    remover.select_percent = select_percent
    remover.remove_percent = remove_percent
    remover.rot_min = rot_min
    remover.rot_max = rot_max
    remover.tilt_min = tilt_min
    remover.tilt_max = tilt_max
    remover.particle_number_threshold = particle_number_threshold  # bigger than this value is selected else kept
    return remover.run()
    # step003 end


# 4 integrate end
if __name__ == '__main__':
    """
    usage:
        change 'star_file' as original star file
        change 'output_dir' for multiple star file generation
        if output_dir does not exist, new dir will be created.
        
        jupyter lab will be helpful.
    
    
    """
    star_file = './data/run_data.star'

    final_data_list, output_dir = parse_and_preview(star_file)

    new_star_file_output_dir = output_dir

    new_star_file = fix_euler_distribution(star_file=star_file,
                                           output_dir=new_star_file_output_dir,
                                           final_data_list=final_data_list,
                                           rot_min=-200.0,
                                           rot_max=+200.0,
                                           tilt_min=-1.0,
                                           tilt_max=+ 200.0,
                                           remove_percent=0.3,
                                           select_percent=0.2,  # when auto_mode=False,this value will be ignored
                                           particle_number_threshold=-1,
                                           # bigger than this value is selected else removed
                                           auto_mode=False,
                                           )

    final_data_list, output_dir = parse_and_preview(new_star_file)
