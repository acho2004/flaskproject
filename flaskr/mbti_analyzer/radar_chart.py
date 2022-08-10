import random
import pandas as pd
from math import pi
from matplotlib import pyplot as plt
from .config import *

labels = Filter.CAP

def get_radarchart_one(data_df: pd.DataFrame, employee_num: str, output_path: str) -> None:

    num_labels = len(labels)

    angles = [x / float(num_labels) * (2 * pi) for x in range(num_labels)]  ## 각 등분점
    angles += angles[:1]  ## 시작점으로 다시 돌아와야하므로 시작점 추가
    my_palette = plt.cm.get_cmap("Set2", 100)

    fig = plt.figure(figsize=(15, 15))
    fig.set_facecolor('white')

    color = my_palette(random.randint(0, 100))
    data = data_df[1:].tolist()
    data += data[:1]

    ax = plt.subplot(1, 1, 1, polar=True)
    ax.set_theta_offset(pi / 2)  ## 시작점
    ax.set_theta_direction(-1)  ## 그려지는 방향 시계방향

    plt.xticks(angles[:-1], labels, fontsize=15)  ## x축 눈금 라벨
    ax.tick_params(axis='x', which='major', pad=15)  ## x축과 눈금 사이에 여백을 준다.

    ax.set_rlabel_position(0)  ## y축 각도 설정(degree 단위)
    plt.yticks([0, 1, 2, 3, 4, 5], ['0', '1', '2', '3', '4', '5'], fontsize=10)  ## y축 눈금 설정
    plt.ylim(0, 5)

    ax.plot(angles, data, color=color, linewidth=2, linestyle='solid')  ## 레이더 차트 출력
    ax.fill(angles, data, color=color, alpha=0.4)  ## 도형 안쪽에 색을 채워준다.

    plt.title(data_df[0], pad=50, fontsize=20)  ## 타이틀은 리더 id
    plt.savefig(os.path.join(output_path, '{0}_radarchart.png'.format(employee_num)))
    plt.close(fig)