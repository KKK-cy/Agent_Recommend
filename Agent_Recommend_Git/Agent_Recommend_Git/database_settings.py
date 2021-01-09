# -*- coding:utf-8 -*-
# @Time : 2021/1/7 15:26
# @Author : KCY
# @File : database_settings.py
# @Software: PyCharm


"""
    数据库参数配置文件
"""

import sqlalchemy
import pandas as pd


class DatabaseSettings(object):
    def __init__(self):
        # 库名
        self.database_name = "agent_recommend"

        # 含8个指标数据的结果表
        self.final_result_table = "final_result"

        # 分词结果分类表
        self.fenci_result_fenlei_table = "fenci_result_fenlei"

        # 推荐总得分表
        self.recommend_score = "recommend_score"

        # 次要推荐依据表
        self.recommend_second_table = "recommend_second"

    # 写入数据库相关函数
    def get_engine(self):
        return sqlalchemy.create_engine("mysql+pymysql://root:1@localhost:3306/" + self.database_name)

    def csv_to_database(self, engine, file_name, database_name, table_name):
        df = pd.read_csv(file_name, encoding="utf-8")
        try:
            df.to_sql(table_name, engine, index=False)
            # print("{file_name}文件已写入{database_name}的{table_name}表".format(file_name=file_name, database_name=database_name, table_name=table_name))
        except ValueError:
            # 表已存在，删除并重新写入
            engine.execute("drop table if exists %s" % table_name)
            df.to_sql(table_name, engine, index=False)
            # print("表{table_name}已存在，删除并重新插入{file_name}的数据".format(table_name=table_name,file_name=file_name))

    # 从数据库的某张表中查询数据
    def get_agent_info(self, engine, table_name):
        sql = """ select * from  {table_name}""".format(table_name=table_name)
        df = pd.read_sql_query(sql, engine)
        return df

    # 将df 存入数据库的某张表中
    def save_to_database(self, df, engine, table_name):
        # 若表已存在，就删除后重新插入
        try:
            df.to_sql(table_name, engine, index=False)
            # print("{file_name}文件已写入{database_name}的{table_name}表".format(file_name=file_name, database_name=database_name, table_name=table_name))
        except ValueError:
            # 表已存在，删除并重新写入
            engine.execute("drop table if exists %s" % table_name)
            print("{table_name}已删除，将重新插入数据".format(table_name=table_name))
            df.to_sql(table_name, engine, index=False)
            # print("表{table_name}已存在，删除并重新插入{file_name}的数据".format(table_name=table_name,file_name=file_name))

