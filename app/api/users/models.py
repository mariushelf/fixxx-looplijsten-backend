import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from api.users.user_manager import UserManager
from api.users.utils import generate_username

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        blank=False,
        error_messages={
            'unique': "A user with that email already exists.",
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def full_name(self):
        '''
        Parses and returns last name from email (f.foo will return foo)
        '''
        if self.email:
            split_email_username = self.email.split('@')[0].split('.')
            if len(split_email_username) == 2:
                first_initial = split_email_username[0]
                first_initial = first_initial.capitalize()

                last_name = split_email_username[1]
                last_name = last_name.capitalize()

                return '{}. {}'.format(first_initial, last_name)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        self.username = generate_username(self.email)
        super().save(*args, **kwargs)
