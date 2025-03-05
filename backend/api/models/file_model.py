from django.db import models


class File(models.Model):
    file_name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'files'
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return self.file_name