# Generated by Django 3.0.3 on 2020-05-06 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agents_comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent_id', models.IntegerField(default='中介ID')),
                ('agent_name', models.CharField(default='中介姓名', max_length=60)),
                ('comment', models.CharField(default='中介评论', max_length=300)),
                ('star_score', models.IntegerField(default='评分')),
            ],
        ),
        migrations.CreateModel(
            name='Agents_other_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent_id', models.IntegerField(default='中介ID')),
                ('agent_name', models.CharField(default='中介姓名', max_length=60)),
                ('agent_url', models.CharField(default='中介个人主页', max_length=100)),
                ('service_year', models.IntegerField(default='服务年限')),
                ('sale_number', models.IntegerField(default='卖房数量')),
                ('rent_number', models.IntegerField(default='租赁数量')),
                ('kanfang_number_30_days', models.IntegerField(default='30天内带看房数量')),
                ('followers_number', models.IntegerField(default='关注人数')),
                ('on_time', models.IntegerField(default='神准时个数')),
                ('walking_map', models.IntegerField(default='活地图个数')),
                ('good_service', models.IntegerField(default='服务好个数')),
                ('positive_energy', models.IntegerField(default='正能量个数')),
                ('warm_heart', models.IntegerField(default='热心肠个数')),
                ('professional_work', models.IntegerField(default='专业个数')),
                ('comments_number', models.IntegerField(default='评论条数')),
                ('phone_number', models.CharField(default='电话号码', max_length=60)),
                ('sales_num_every_year', models.FloatField(default='平均每年卖房数量')),
                ('rent_num_every_year', models.FloatField(default='平均每年租赁房屋数量')),
                ('on_time_percent', models.FloatField(default='神准时占比')),
                ('walking_map_percent', models.FloatField(default='活地图占比')),
                ('good_service_percent', models.FloatField(default='服务好占比')),
                ('positive_energy_percent', models.FloatField(default='正能量占比')),
                ('warm_heart_percent', models.FloatField(default='热心肠占比')),
                ('professional_work_percent', models.FloatField(default='专业占比')),
                ('avg_biaoqian_percent', models.FloatField(default='平均标签占比')),
            ],
        ),
    ]