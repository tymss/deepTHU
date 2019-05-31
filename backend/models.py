from django.db import models


class Task(models.Model):

    task_id = models.CharField(primary_key=True, max_length=32, unique=True)
    training_time = models.IntegerField()
    email = models.CharField(max_length=256, blank=True)
    dst_format = models.CharField(max_length=32, default='mp4')
    state = models.CharField(max_length=32, default='CREATING')
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_table'
        ordering = ['create_time']

    def __str__(self):
        return self.task_id

