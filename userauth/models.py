from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
import string
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn
import time

# Algod client setup
ALGOD_ADDRESS = 'http://localhost:4001'  # Adjust as per sandbox setup
ALGOD_TOKEN = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'  # Sandbox default

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Sandbox test account details with mnemonic
SENDER_ADDRESS = "CFJYTKAYUAQJJY4BO3ZBBS6JZSZCYW36GOYZIJR5RSZQZIWYOBXVA5OBDI"
SENDER_MNEMONIC = "reward abandon essence globe velvet leaf barely olympic margin wasp portion bonus fine call job typical vintage neutral dumb salute test lens render absorb axis"
SENDER_PRIVATE_KEY = mnemonic.to_private_key(SENDER_MNEMONIC)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        # Generate Algorand account for the user
        private_key, address = account.generate_account()
        extra_fields['wallet_address'] = address
        extra_fields['algorand_private_key'] = private_key

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Automatically transfer 1000 microAlgos to the new account
        self._fund_new_account(address)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)

    def _fund_new_account(self, receiver_address):
        # Set up a payment transaction
        params = algod_client.suggested_params()
        transaction = PaymentTxn(
            sender=SENDER_ADDRESS,
            sp=params,
            receiver=receiver_address,
            amt=1000  # 1000 microAlgos = 0.001 Algos
        )

        # Sign and send the transaction
        signed_txn = transaction.sign(SENDER_PRIVATE_KEY)
        txid = algod_client.send_transaction(signed_txn)
        print(f"Transaction sent with txID: {txid}")

        # Wait for confirmation
        try:
            confirmed_txn = self._wait_for_confirmation(txid)
            print("Transaction confirmed in round:", confirmed_txn.get('confirmed-round', ""))
        except Exception as e:
            print(f"Error confirming transaction: {e}")

    def _wait_for_confirmation(self, txid):
        """Utility function to wait until the transaction is confirmed."""
        last_round = algod_client.status().get('last-round')
        while True:
            txinfo = algod_client.pending_transaction_info(txid)
            if txinfo.get('confirmed-round', 0) > 0:
                return txinfo
            print("Waiting for confirmation...")
            last_round += 1
            algod_client.status_after_block(last_round)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    TAILOR = 'TAILOR'
    CUSTOMER = 'CUSTOMER'
    ROLE_CHOICES = [
        (TAILOR, 'Tailor'),
        (CUSTOMER, 'Customer'),
    ]

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = [
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=CUSTOMER,
        help_text="Role of the user, either Tailor or Customer."
    )
    customer_id = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique identifier for customers, 6 characters."
    )
    wallet_address = models.CharField(
        max_length=58,
        blank=True,
        null=True,
        help_text="Algorand wallet address for transactions."
    )
    algorand_private_key = models.TextField(blank=True, null=True, help_text="Algorand private key, securely stored.")
    customers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='tailors',
        blank=True,
        help_text="Customers associated with a tailor."
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Generate a 6-character unique customer_id only for customers if not already set
        if self.role == self.CUSTOMER and not self.customer_id:
            self.customer_id = self.generate_customer_id()

        # Generate Algorand account if wallet details are missing
        if not self.wallet_address or not self.algorand_private_key:
            private_key, address = account.generate_account()
            self.wallet_address = address
            self.algorand_private_key = private_key

        super().save(*args, **kwargs)

    @staticmethod
    def generate_customer_id():
        # Generate a random 6-character alphanumeric ID
        while True:
            customer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not CustomUser.objects.filter(customer_id=customer_id).exists():
                return customer_id
