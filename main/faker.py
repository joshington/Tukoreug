from faker import Faker
fake = Faker()

#first, import a similar Provider or use the default one


from faker.providers import BaseProvider,DynamicProvider

#create new provider class
class MyProvider(BaseProvider):
    def foo(self) -> str:return 'bar'

#then add new provider to faker instance
fake.add_provider(MyProvider)
#NOW YOU can use:
fake.foo() #==returns 'bar'

#===dynamic providers can read elements from an external source
medical_professions_provider = DynamicProvider(
    provider_name="medical_profession",
    elements=["dr.","doctor","nurse","surgeon","clerk"],
)

fake=Faker()
#==then add new provider to Faker instance
fake.add_provider(medical_professions_provider)
#==now you can use:
fake.medical_profession() #'dr'

#==using with Factory Boy
#===Factory Boy ships with integration with Faker. use the factory.Faker method of factory_boy
import factory
from .models import*

class UserFactory(factory.Factory):
    class Meta:
        model = Testimonials
    name=factory.Faker('name')
    amount = factory.Faker('amount')


