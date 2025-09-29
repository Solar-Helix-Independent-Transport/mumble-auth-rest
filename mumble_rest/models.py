import logging

from django.db import models
from secrets import SystemRandom
from passlib.hash import pbkdf2_sha256
from django.contrib.auth.hashers import identify_hasher, make_password, check_password
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

def generate_token(length=50, chars=UNICODE_ASCII_CHARACTER_SET):
    """Generates a non-guessable OAuth token

    OAuth (1 and 2) does not specify the format of tokens except that they
    should be strings of random characters. Tokens should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = SystemRandom()
    return ''.join(rand.choice(chars) for _ in range(length))

class ClientSecretField(models.CharField):
    def pre_save(self, model_instance, add):
        secret = getattr(model_instance, self.attname)
        try:
            hasher = identify_hasher(secret)
            logger.debug(f"{model_instance}: {self.attname} is already hashed with {hasher}.")
        except ValueError:
            logger.debug(f"{model_instance}: {self.attname} is not hashed; hashing it now.")
            
            hashed_secret = make_password(secret)
            test = check_password(secret, hashed_secret)
            print(test)
            setattr(model_instance, self.attname, hashed_secret)
            return hashed_secret
        return super().pre_save(model_instance, add)

class APIKey(models.Model):
    name = models.CharField(max_length=250)
    token = ClientSecretField(
        max_length=255,
        blank=True,
        default=generate_token,
        db_index=True,
        help_text=_("Hashed on Save. Copy it now if this is a new secret."),
    )
    
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        default_permissions = []

    def __str__(self):
        return f'{self.name} - {self.token[:10]}'

    def test(self, password):
        return check_password(password, self.token)