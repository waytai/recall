import uuid
from example import locators as l

import recall.models as m
import recall.event_handler as eh


class CompanyFounded(m.Event):
    def require(self, guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(name, str)


class WhenCompanyFounded(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, CompanyFounded)
        self.entity.guid = event['guid']
        self.entity.name = event['name']


class EmployeeHired(m.Event):
    def require(self, guid, employee_guid, name, title):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(employee_guid, uuid.UUID)
        assert isinstance(name, str)
        assert isinstance(title, str)


class WhenEmployeeHired(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, EmployeeHired)
        employee = Employee(
            event['employee_guid'],
            event['name'],
            event['title'])
        self.entity.employees.add(employee)


class EmployeePromoted(m.Event):
    def require(self, guid, title):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(title, str)


class WhenEmployeePromoted(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, EmployeePromoted)
        self.entity.title = event['title']


class FoundCompany(m.Command):
    def require(self, name):
        assert isinstance(name, str)


class HireEmployee(m.Command):
    def require(self, name, title):
        assert isinstance(name, str)
        assert isinstance(title, str)


class PromoteEmployee(m.Command):
    def require(self, title):
        assert isinstance(title, str)


class Company(m.AggregateRoot):
    def __init__(self):
        super(Company, self).__init__()
        self.name = None
        self.employees = m.EntityList()
        self._register_handlers()

    def found(self, command):
        assert isinstance(command, FoundCompany)
        name = command.get("name")
        if name:
            self._apply_event(CompanyFounded(
                guid=self._create_guid(),
                name=name))

    def hire_employee(self, command):
        assert isinstance(command, HireEmployee)
        name = command.get("name")
        title = command.get("title")
        if self.is_founded() and name and title:
            employee = self._create_guid()
            self._apply_event(EmployeeHired(
                guid=self.guid,
                employee_guid=employee,
                name=name,
                title=title))
            return employee

    def is_founded(self):
        return bool(self.guid)

    def _register_handlers(self):
        self._register_event_handler(CompanyFounded, WhenCompanyFounded)
        self._register_event_handler(EmployeeHired, WhenEmployeeHired)


class Employee(m.Entity):
    def __init__(self, guid, name, title):
        super(Employee, self).__init__()
        self.guid = guid
        self.name = name
        self.title = title
        self._register_handlers()

    def promote(self, command):
        assert isinstance(command, PromoteEmployee)
        title = command.get("title")
        if title:
            self._apply_event(EmployeePromoted(guid=self.guid, title=title))

    def _register_handlers(self):
        self._register_event_handler(EmployeePromoted, WhenEmployeePromoted)


def main():
    # Perform some commands
    company = Company()
    company.found(FoundCompany(name="Planet Express"))
    company.hire_employee(HireEmployee(name="Turanga Leela", title="Captain"))
    fry = company.hire_employee(HireEmployee(
        name="Philip Fry",
        title="Delivery Boy"))
    company.employees.get(fry).promote(PromoteEmployee(title="Narwhal Trainer"))

    # Save AR
    repo = l.RepositoryLocator().locate(Company)
    repo.save(company)
    guid = company.guid
    del company

    # Load AR
    company = repo.load(guid)
    print(company.name)
    for employee in company.employees.values():
        print(" - %s, %s" % (employee.name, employee.title))

main()
