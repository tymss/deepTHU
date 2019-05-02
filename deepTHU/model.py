from django.db import models

state_list = ['CREATING', 'CREATED', 'RUNNING', 'FINISHED', 'FAILED']

class Task(models.Model):

    task_id = models.CharField(primary_key=True, max_length=20, unique=True)
    state = models.CharField(max_length=20, choices=state_list)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_table'
        ordering = ['create_time']

    def __str__(self):
        return self.task_id

