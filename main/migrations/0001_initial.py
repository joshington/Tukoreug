# Generated by Django 2.2 on 2023-02-15 10:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='bosa', max_length=254)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=254)),
                ('paid', models.BooleanField(default=False)),
                ('ref_code', models.CharField(max_length=12)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('ref_link', models.URLField()),
                ('account_type', models.CharField(choices=[('SILVER', 'Silver'), ('GOLD', 'Gold'), ('PLATINUM', 'Platinum')], default='SILVER', max_length=8)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'unique_together': {('username', 'email')},
            },
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.PositiveIntegerField(default=0)),
                ('deposits', models.PositiveIntegerField(default=0)),
                ('widthdraws', models.PositiveIntegerField(default=0)),
                ('nousers', models.IntegerField(default=0)),
                ('no_active_users', models.IntegerField(default=0)),
                ('profits', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Testimonials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='mapeera', max_length=15)),
                ('amount', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Child',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_child', models.BooleanField(default=False)),
                ('is_grandchild', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_parent', models.BooleanField(default=False)),
                ('is_grandparent', models.BooleanField(default=False)),
                ('no_children', models.IntegerField(default=0)),
                ('no_grand_children', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('balance', models.PositiveIntegerField(default=0)),
                ('earnings', models.PositiveIntegerField(default=0)),
                ('bonus', models.PositiveIntegerField(default=0)),
                ('withdraws', models.PositiveIntegerField(default=0)),
                ('owner', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('COMPLETE', 'Complete'), ('FAILED', 'Failed')], default='PENDING', max_length=8)),
                ('transaction_ref', models.UUIDField(default=uuid.uuid4)),
                ('amount', models.IntegerField()),
                ('category', models.CharField(choices=[('TOP_UP', 'Top Up'), ('WITHDRAW', 'Withdraw')], default='TOP_UP', max_length=8)),
                ('user', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GrandParent',
            fields=[
                ('user', models.OneToOneField(default='user1', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('child_parent', models.ForeignKey(default='parent1', on_delete=django.db.models.deletion.PROTECT, to='main.Parent')),
                ('grand_child', models.ForeignKey(default='child1', on_delete=django.db.models.deletion.PROTECT, to='main.Child')),
            ],
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Parent'),
        ),
    ]
