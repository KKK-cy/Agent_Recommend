# -*- coding: utf-8 -*-

"""
    # @Author : Administrator
    # @Time : 2020/4/21 22:14
    脚本说明：
        1. 对评论进行分词，统计所有词语的出现次数
        2. 选出出现次数最高的前250个词语，手动从中筛选出常见的程度副词并给定权重值
"""
import jieba
import pandas as pd
from tqdm import tqdm
from ..seetings import stopwordslist, stopwords_in_path, save_as_csv, top_250_word_path, degreewordslist, degree_in_path, \
    nowordslist, no_in_path

"""---------------------------- 2. 统计词语出现次数，获取常见的程度副词词典和中介-词语矩阵 -----------------"""
# 对某条评论进行分词
def segComment(sentence, stopwords):
    # 添加自定义词语
    wordslist = ['靠谱', '能力强']
    for i in wordslist:
        jieba.add_word(i)
    sentence_seg = jieba.cut(sentence.strip())
    outstr = ''
    # 去除停用词
    for word in sentence_seg:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += ' '

    for word in sentence_seg:
        outstr += word
        outstr += " "
    return outstr

# 分词函数（输入：分词前的评论文件，分词结果文件）
def fenci(fileinpath, fileoutpath):
    print("2.1 开始分词 ",end=" ,")
    agent_info_df = pd.read_csv(fileinpath)
    stopwords = stopwordslist(stopwords_in_path)
    final_result_df = pd.DataFrame()
    agent_list = list(set(list(agent_info_df["agent_id"])))

    # 遍历每个中介
    for agent_id in tqdm(agent_list):
        agent_df = agent_info_df.loc[agent_info_df["agent_id"] == agent_id]
        agent_df["seg_comment_result"] = ""
        seg_comment_list = []
        # 遍历该中介的每条评论
        for comment in agent_df["comment"]:
            seg_comment = segComment(comment, stopwords)
            seg_comment_list.append(seg_comment)
        agent_df["seg_comment_result"] = seg_comment_list
        # 将该中介的分词结果保存进总结果中
        final_result_df = final_result_df.append(agent_df, sort=False)

    save_as_csv(final_result_df, fileoutpath)
    print("分词完成，分词结果已保存至文件 %s " % fileoutpath)



# 读取分词结果文件，统计所有词语的出现次数
def get_all_words(fileinpath):
    # print("2.2 开始统计所有词语的出现次数")
    data = pd.read_csv(fileinpath)

    fenci_result_df = data["seg_comment_result"]
    comments_word_list = fenci_result_df.tolist()
    all_words = []
    all_words_times = {}
    for comment_word in comments_word_list:
        comment_word = str(comment_word)
        # 将每条评论中的分词结果变为列表形式
        comment_word_list = comment_word.split(" ")
        for word in comment_word_list:
            if word not in all_words and word != "":
                all_words.append(word)
    # print("共有 %d 个词语" % len(all_words), end=" ,")

    # 将所有词语转化为字典，初始值给0
    all_words_times = all_words_times.fromkeys(all_words, 0)
    # 遍历每条评论，获取到词语出现的总次数
    for comment_word in comments_word_list:
        comment_word = str(comment_word)
        # 将每条评论中的分词结果变为列表形式
        comment_word_list = comment_word.split(" ")
        for word in comment_word_list:
            if word in all_words_times.keys():
                all_words_times[word] += 1
    result = sorted(all_words_times.items(), key=lambda x: x[1], reverse=True)
    # print("所有词语的出现总次数由高到低排序为：%s " % result)
    return result


def get_top_k_words(result, degree_nums):
    # 前num个词语
    final_result = result[:(degree_nums)]
    top_k_words = {}
    for i in final_result:
        top_k_words[i[0]] = i[1]
    top_k_words_list = list(top_k_words.keys())
    # print("出现次数最高的前 %s 个词语为： %s " % (degree_nums, str(top_k_words_list)))
    return top_k_words_list


def get_degree_words(result, degree_nums):
    print("2.3 从出现次数最高的前 %d 个词语中产生常见的程度副词词典：" % degree_nums)
    # 根据分词结果获取到出现次数最高的前k个词语
    top_n_word = get_top_k_words(result, degree_nums)
    # 将前250个词语写入文件
    file = open(top_250_word_path, "w")
    file.write("\n".join(top_n_word))
    file.close()
    print("前 %s 个词语已写入文件 %s ，接下来请手动从中筛选出常见的程度副词并给定权值..." % (degree_nums, top_250_word_path))


"""获取中介-词语矩阵"""
def get_agent_juzhen(fileinpath, result, number):
    data = pd.read_csv(fileinpath)
    agent_id_list = list(set(data["agent_id"].tolist()))

    top_k_words_list = get_top_k_words(result, number)
    degree_words, degree_dict = degreewordslist(degree_in_path)
    no_words = nowordslist(no_in_path)

    for k_word in top_k_words_list:
        if k_word in degree_words:
            # print("%s在程度副词中，需要删除..." % k_word)
            top_k_words_list.remove(k_word)
        elif k_word in no_words:
            # print("%s在否定词中，需要删除..." % k_word)
            top_k_words_list.remove(k_word)
    print("最终产生的{num}个词语为{words}".format(num=len(top_k_words_list),words=top_k_words_list))

    all_agent_result = []
    for agent_id in agent_id_list:
        agent_result = {}
        agent_result = agent_result.fromkeys(top_k_words_list, 0)
        agent_data = data[data["agent_id"] == agent_id]
        agent_data_fenci = agent_data["seg_comment_result"].tolist()

        """获取该中介的所有评论中的分词的总个数"""
        word_total_number = 0
        for comment in agent_data_fenci:
            comment = str(comment)
            comment_word_list = comment.split(" ")
            word_total_number += len(comment_word_list)

        # 获取到前k个词每个词语在所有词语中的出现频率
        for comment in agent_data_fenci:
            comment = str(comment)
            comment_word_list = comment.split(" ")
            for word in comment_word_list:
                if word in top_k_words_list:
                    agent_result[word] += round(1 / word_total_number, 3)
        agent_result["agent_id"] = agent_id
        all_agent_result.append(agent_result)

    top_k_words_list.append("agent_id")
    agent_df = pd.DataFrame(all_agent_result, columns=top_k_words_list)
    print("产生中介-词语矩阵成功！")
    return agent_df