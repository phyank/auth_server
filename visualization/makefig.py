import numpy as np
import matplotlib
from wordcloud import WordCloud

matplotlib.use('Agg') #by default, the backend of matplotlib depends on GUI. Use Agg instead.

import matplotlib.pyplot

# 传入的vector是float数组，数组元素0-1之间
# path是图片保存路径
def create_vector_graph(vector,path):
    N = len(vector)
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    vector = np.array(vector)
    radii = vector
    width = np.pi / N

    ax = matplotlib.pyplot.subplot(111, projection='polar')
    ax.axes.get_yaxis().set_ticklabels([])
    bars = ax.bar(theta, radii, width=width, bottom=0.0)

    for r, bar in zip(radii, bars):
        bar.set_facecolor(matplotlib.pyplot.cm.gnuplot(r))
        bar.set_alpha(0.8)

    try:
        matplotlib.pyplot.savefig(path)
        return 0
        # 用于显示图片
        # plt.show()
    except Exception as e:
        print('vector graph save failed\n',e)
        return -1

# 传入的text是utf-8编码的中文字符串，每个词之间用空格分开
# path为图片保存路径
def create_wordcloud(text,path):
    try:
        bg = matplotlib.pyplot._imread('visualization/background.jpg')
    except:
        print('read background picture failed')
        return -1
    wc = WordCloud(font_path="visualization/msyh.ttc", mask=bg, background_color='white', max_font_size=80)
    wc.generate(text)

    wc.to_file(path)
    # 用于显示图片
    # plt.imshow(wc)
    # plt.axis('off')
    # plt.show()
    return 0
