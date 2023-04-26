from users.models import User

user = User.objects.create(
    username='johndoe',
    email='johndoe@example.com',
    password='password',
    first_name='John',
    last_name='Doe',
    is_verified_email=True,
    is_matched=False,
)
