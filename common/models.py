from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RecordBaseModel(BaseModel):
    create_user_id = models.IntegerField(null=True, blank=True)
    update_user_id = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True
