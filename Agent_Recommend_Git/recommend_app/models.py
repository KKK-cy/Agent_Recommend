from django.db import models


# Create your models here.
class Agents_other_info(models.Model):
    agent_id = models.IntegerField(default='中介ID')
    agent_name = models.CharField(default='中介姓名', max_length=60)
    agent_url = models.CharField(default='中介个人主页', max_length=100)

    service_year = models.IntegerField(default='服务年限')
    sale_number = models.IntegerField(default='卖房数量')
    rent_number = models.IntegerField(default='租赁数量')
    kanfang_number_30_days = models.IntegerField(default='30天内带看房数量')
    followers_number = models.IntegerField(default='关注人数')

    on_time = models.IntegerField(default='神准时个数')
    walking_map = models.IntegerField(default='活地图个数')
    good_service = models.IntegerField(default='服务好个数')
    positive_energy = models.IntegerField(default='正能量个数')
    warm_heart = models.IntegerField(default='热心肠个数')
    professional_work = models.IntegerField(default='专业个数')
    comments_number = models.IntegerField(default='评论条数')

    phone_number = models.CharField(default='电话号码', max_length=60)
    agent_img = models.CharField(default='中介图片', max_length=60)


    sales_num_every_year = models.FloatField(default='平均每年卖房数量')
    rent_num_every_year = models.FloatField(default='平均每年租赁房屋数量')
    on_time_percent = models.FloatField(default='神准时占比')
    walking_map_percent = models.FloatField(default='活地图占比')
    good_service_percent = models.FloatField(default='服务好占比')
    positive_energy_percent = models.FloatField(default='正能量占比')
    warm_heart_percent = models.FloatField(default='热心肠占比')
    professional_work_percent = models.FloatField(default='专业占比')
    avg_biaoqian_percent = models.FloatField(default='平均标签占比')


class Agents_comments(models.Model):
    agent_id = models.IntegerField(default='中介ID')
    agent_name = models.CharField(default='中介姓名', max_length=60)
    comment = models.CharField(default='中介评论', max_length=300)
    star_score = models.IntegerField(default='评分')

# 用户注册类
class User(models.Model):
    '''用户表'''

    gender = (
        ('male','男'),
        ('female','女'),
    )

    name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32,choices=gender,default='男')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Agent_scores(models.Model):
    agent_id = models.IntegerField(default='中介ID')
    agent_name = models.CharField(default='中介姓名', max_length=60)
    agent_img = models.CharField(default='中介图片', max_length=60)
    agent_url = models.CharField(default='中介个人主页', max_length=100)
    # 原始评分均值
    original_avg_score = models.FloatField(default='原始评分均值')
    # 评论文本情感得分值均值
    emotion_avg_score = models.FloatField(default='评论文本情感得分均值')

# 中介-情感矩阵表
class Agent_emotion_juzhen(models.Model):
    agent_id = models.IntegerField(default='中介ID')
    agent_name = models.CharField(default='中介姓名', max_length=60)
    agent_img = models.CharField(default='中介图片', max_length=60)
    agent_url = models.CharField(default='中介个人主页', max_length=100)

    zhuanye = models.FloatField(default='专业')
    jingjiren = models.FloatField(default='经纪人')
    fuwu = models.FloatField(default='服务')
    fangzi = models.FloatField(default='房子')
    reqing = models.FloatField(default='热情')
    yewu = models.FloatField(default='业务')
    bucuo = models.FloatField(default='不错')
    kaopu = models.FloatField(default='靠谱')
    kanfang = models.FloatField(default='看房')
    fangyuan = models.FloatField(default='房源')
    recommend_score = models.CharField(default='推荐总得分', max_length=100)