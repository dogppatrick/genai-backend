import logging

from django.core.cache import cache
from rest_framework.test import APITestCase


class ViewTestCase(APITestCase):
    def setUp(self):
        # 設定 log level 避免無謂的警告訊息
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        cache.clear()

    def tearDown(self):
        # 重設 log level
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)

        cache.clear()
