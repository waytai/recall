import datetime as dt
import json
import optparse
import random
import uuid

import yaml

import recall.event_handler as eh
import recall.models as m
import recall.locators as l

accounts = []
accounts_with_campaigns = []
accounts_with_campaigns_with_mailings = []
addresses = []
counts = {}


class CreateAccount(m.Command):
    def require(self, name):
        assert isinstance(name, basestring)


class ChangeAccountName(m.Command):
    def require(self, name):
        assert isinstance(name, basestring)


class ChangeCampaignName(m.Command):
    def require(self, name):
        assert isinstance(name, basestring)


class AddAccountMember(m.Command):
    def require(self, address):
        assert isinstance(address, basestring)


class AddAccountCampaign(m.Command):
    def require(self, name):
        assert isinstance(name, basestring)


class SendCampaignMailing(m.Command):
    def require(self, name):
        assert isinstance(name, basestring)


class OpenMailing(m.Command):
    def require(self, datetime, address):
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class ClickMailing(m.Command):
    def require(self, datetime, address):
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class ShareMailing(m.Command):
    def require(self, datetime, address):
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class AccountCreated(m.Event):
    def require(self, guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(name, basestring)


class AccountNameChanged(m.Event):
    def require(self, guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(name, basestring)


class CampaignNameChanged(m.Event):
    def require(self, guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(name, basestring)


class AccountMemberAdded(m.Event):
    def require(self, guid, address):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(address, basestring)


class AccountCampaignAdded(m.Event):
    def require(self, guid, campaign_guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(campaign_guid, uuid.UUID)
        assert isinstance(name, basestring)


class CampaignMailingSent(m.Event):
    def require(self, guid, mailing_guid, name):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(mailing_guid, uuid.UUID)
        assert isinstance(name, basestring)


class MailingOpened(m.Event):
    def require(self, guid, datetime, address):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class MailingClicked(m.Event):
    def require(self, guid, datetime, address):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class MailingShared(m.Event):
    def require(self, guid, datetime, address):
        assert isinstance(guid, uuid.UUID)
        assert isinstance(datetime, dt.datetime)
        assert isinstance(address, basestring)


class WhenAccountCreated(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, AccountCreated)
        self.entity.guid = event['guid']
        self.entity.name = event['name']


class WhenAccountNameChanged(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, AccountNameChanged)
        self.entity.name = event['name']


class WhenCampaignNameChanged(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, CampaignNameChanged)
        self.entity.name = event['name']


class WhenAccountMemberAdded(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, AccountMemberAdded)
        self.entity.members.append(event['address'])


class WhenAccountCampaignAdded(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, AccountCampaignAdded)
        campaign = Campaign(event["campaign_guid"], event["name"])
        self.entity.campaigns.add(campaign)


class WhenCampaignMailingSent(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, CampaignMailingSent)
        mailing = Mailing(event["mailing_guid"], event["name"])
        self.entity.mailings.add(mailing)


class WhenMailingOpened(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, MailingOpened)
        if event["address"] not in self.entity.engaged:
            self.entity.engaged.append(event["address"])


class WhenMailingClicked(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, MailingClicked)
        if event["address"] not in self.entity.engaged:
            self.entity.engaged.append(event["address"])


class WhenMailingShared(eh.DomainEventHandler):
    def __call__(self, event):
        assert isinstance(event, MailingShared)
        if event["address"] not in self.entity.engaged:
            self.entity.engaged.append(event["address"])


class Account(m.AggregateRoot):
    def __init__(self):
        super(Account, self).__init__()
        self.name = None
        self.members = []
        self.campaigns = m.EntityList()
        self._register_handlers()

    def is_created(self):
        return bool(self.guid)

    def create(self, command):
        assert isinstance(command, CreateAccount)
        name = command.get("name")
        if not self.is_created() and name:
            self._apply_event(AccountCreated(
                guid=self._create_guid(),
                name=name))

    def change_name(self, command):
        assert isinstance(command, ChangeAccountName)
        name = command.get("name")
        if self.is_created() and name:
            self._apply_event(AccountNameChanged(guid=self.guid, name=name))

    def add_member(self, command):
        assert isinstance(command, AddAccountMember)
        address = command.get("address")
        if self.is_created() and address:
            self._apply_event(AccountMemberAdded(
                guid=self.guid,
                address=address))

    def add_campaign(self, command):
        assert isinstance(command, AddAccountCampaign)
        name = command.get("name")
        if self.is_created() and name:
            campaign = self._create_guid()
            self._apply_event(AccountCampaignAdded(
                guid=self.guid,
                campaign_guid=campaign,
                name=name))

    def _register_handlers(self):
        self._register_event_handler(
            AccountCreated,
            WhenAccountCreated)
        self._register_event_handler(
            AccountNameChanged,
            WhenAccountNameChanged)
        self._register_event_handler(
            AccountMemberAdded,
            WhenAccountMemberAdded)
        self._register_event_handler(
            AccountCampaignAdded,
            WhenAccountCampaignAdded)


class Campaign(m.Entity):
    def __init__(self, guid, name):
        super(Campaign, self).__init__()
        self.guid = guid
        self.name = name
        self.mailings = m.EntityList()
        self._register_handlers()

    def change_name(self, command):
        assert isinstance(command, ChangeCampaignName)
        name = command.get("name")
        if name:
            self._apply_event(CampaignNameChanged(
                guid=self.guid,
                name=name))

    def send_mailing(self, command):
        assert isinstance(command, SendCampaignMailing)
        name = command.get("name")
        if name:
            mailing = self._create_guid()
            self._apply_event(CampaignMailingSent(
                guid=self.guid,
                mailing_guid=mailing,
                name=name))

    def _register_handlers(self):
        self._register_event_handler(
            CampaignNameChanged,
            WhenCampaignNameChanged)
        self._register_event_handler(
            CampaignMailingSent,
            WhenCampaignMailingSent)


class Mailing(m.Entity):
    def __init__(self, guid, name):
        super(Mailing, self).__init__()
        self.guid = guid
        self.name = name
        self.engaged = []
        self._register_handlers()

    def open(self, command):
        assert isinstance(command, OpenMailing)
        address = command.get("address")
        datetime = command.get("datetime")
        if address and datetime:
            self._apply_event(MailingOpened(
                guid=self.guid,
                datetime=datetime,
                address=address))

    def click(self, command):
        assert isinstance(command, ClickMailing)
        address = command.get("address")
        datetime = command.get("datetime")
        if address and datetime:
            self._apply_event(MailingClicked(
                guid=self.guid,
                datetime=datetime,
                address=address))

    def share(self, command):
        assert isinstance(command, ShareMailing)
        address = command.get("address")
        datetime = command.get("datetime")
        if address and datetime:
            self._apply_event(MailingShared(
                guid=self.guid,
                datetime=datetime,
                address=address))

    def _register_handlers(self):
        self._register_event_handler(MailingOpened, WhenMailingOpened)
        self._register_event_handler(MailingClicked, WhenMailingClicked)
        self._register_event_handler(MailingShared, WhenMailingShared)


def exec_create_account(repo):
    if counts.get('AccountCreated', 0) < 10:
        counts['AccountCreated'] = counts.get('AccountCreated', 0) + 1
        account = Account()
        account.create(CreateAccount(name="Foo %s" % random.randint(10, 99)))
        repo.save(account)
        accounts.append(account.guid)


def exec_change_account_name(repo):
    if accounts and counts.get('AccountUpdated', 0) < 10:
        counts['AccountUpdated'] = counts.get('AccountUpdated', 0) + 1
        account = repo.load(random.choice(accounts))
        account.change_name(ChangeAccountName(
            name="Foo %s" % random.randint(10, 99)))
        repo.save(account)


def exec_create_address(repo):
    if accounts:
        counts['AddressCreated'] = counts.get('AddressCreated', 0) + 1
        account = repo.load(random.choice(accounts))
        address = random_address()
        account.add_member(AddAccountMember(address=address))
        repo.save(account)
        addresses.append(address)


def exec_create_campaign(repo):
    if accounts and counts.get('CampaignCreated', 0) < 100:
        counts['CampaignCreated'] = counts.get('CampaignCreated', 0) + 1
        account = repo.load(random.choice(accounts))
        account.add_campaign(AddAccountCampaign(
            name="Foo %s" % random.randint(100, 999)))
        repo.save(account)
        accounts_with_campaigns.append(account.guid)


def exec_change_campaign_name(repo):
    if accounts_with_campaigns and counts.get('CampaignCreated', 0) < 10:
        counts['CampaignUpdated'] = counts.get('CampaignUpdated', 0) + 1
        account = repo.load(random.choice(accounts_with_campaigns))
        campaign = random.choice(account.campaigns.values())
        campaign.change_name(ChangeCampaignName(
            name="Foo %s" % random.randint(100, 999)))
        repo.save(account)


def exec_send_mailing(repo):
    if accounts_with_campaigns and counts.get('MailingCreated', 0) < 1000:
        counts['MailingCreated'] = counts.get('MailingCreated', 0) + 1
        account = repo.load(random.choice(accounts_with_campaigns))
        campaign = random.choice(account.campaigns.values())
        campaign.send_mailing(SendCampaignMailing(
            name="Foo %s" % random.randint(1000, 9999)))
        repo.save(account)
        accounts_with_campaigns_with_mailings.append((
            account.guid,
            campaign.guid))


def exec_open_mailing(repo):
    if accounts_with_campaigns_with_mailings and addresses:
        counts['MailingOpened'] = counts.get('MailingOpened', 0) + 1
        account_guid, campaign_guid = random.choice(
            accounts_with_campaigns_with_mailings)
        account = repo.load(account_guid)
        campaign = account.campaigns[campaign_guid]
        mailing = random.choice(campaign.mailings.values())
        mailing.open(OpenMailing(
            datetime=random_time(),
            address=random.choice(addresses)))
        repo.save(account)


def exec_click_mailing(repo):
    if accounts_with_campaigns_with_mailings and addresses:
        counts['MailingClicked'] = counts.get('MailingClicked', 0) + 1
        account_guid, campaign_guid = random.choice(
            accounts_with_campaigns_with_mailings)
        account = repo.load(account_guid)
        campaign = account.campaigns[campaign_guid]
        mailing = random.choice(campaign.mailings.values())
        mailing.click(ClickMailing(
            datetime=random_time(),
            address=random.choice(addresses)))
        repo.save(account)


def exec_share_mailing(repo):
    if accounts_with_campaigns_with_mailings and addresses:
        counts['MailingShared'] = counts.get('MailingShared', 0) + 1
        account_guid, campaign_guid = random.choice(
            accounts_with_campaigns_with_mailings)
        account = repo.load(account_guid)
        campaign = account.campaigns[campaign_guid]
        mailing = random.choice(campaign.mailings.values())
        mailing.share(ShareMailing(
            datetime=random_time(),
            address=random.choice(addresses)))
        repo.save(account)


def random_address():
    return "test+%s@example.com" % str(uuid.uuid4())


def random_time():
    return dt.datetime.now() - dt.timedelta(seconds=random.randint(0, 31536000))


def random_exec(repo):
    return globals()[random.choice(
        [p for p in globals() if p[:5] == "exec_"]
    )](repo)


def get_fqcn(cls):
    return ".".join([cls.__module__, cls.__name__])


def event_count(client, keys):
    def combine_streams(streams, guid):
        return streams + client.lrange(str(guid), 0, -1)

    def aggregate_event(counts, event):
        e = json.loads(event)
        return dict(counts, **{
            e['__type__']:
            (1 if e['__type__'] not in counts else counts[e['__type__']] + 1)})

    events = reduce(combine_streams, keys, [])
    return reduce(aggregate_event, events, {'total': len(events)})


def parse_cli_options():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--count", dest="count", default=10000, type="int",
                      help="Count of random events to generate")

    return parser.parse_args()


def main():
    name = "Tracker Demo"
    settings = yaml.load(open("examples/mailing_tracker.yml", 'r'))
    values, args = parse_cli_options()
    count = values.count
    repo = l.RepositoryLocator(settings).locate(Account)
    repo.event_store._client.flushall()

    print("%s started at %s\n" % (name, dt.datetime.now().isoformat()))

    if count > 1000:
        print("Generating %s random events...this could take a while." % count)

    for i in range(0, count):
        if i and i % 1000 == 0:
            print("Only %s left..." % (count - i))
        random_exec(repo)

    print("\n%s stopped at %s\n\n" % (name, dt.datetime.now().isoformat()))

    stream = event_count(
        repo.event_store._client,
        repo.event_store._client.keys())

    creates = counts.get('AccountCreated', 0)
    updates = counts.get('AccountUpdated', 0)
    print("New Accounts: %s (with %s updates)" % (creates, updates))
    assert creates == stream.get(get_fqcn(AccountCreated))
    assert updates == stream.get(get_fqcn(AccountNameChanged))

    creates = counts.get('CampaignCreated', 0)
    updates = counts.get('CampaignUpdated', 0)
    print("New Campaigns: %s (with %s updates)" % (creates, updates))
    assert creates == stream.get(get_fqcn(AccountCampaignAdded))
    assert updates == stream.get(get_fqcn(CampaignNameChanged))

    creates = counts.get('MailingCreated', 0)
    print("New Mailings: %s" % creates)
    assert creates == stream.get(get_fqcn(CampaignMailingSent))

    creates = counts.get('AddressCreated', 0)
    print("New Addresses: %s" % creates)
    assert creates == stream.get(get_fqcn(AccountMemberAdded))

    creates = counts.get('MailingOpened', 0)
    print("\nOpens: %s" % creates)
    assert creates == stream.get(get_fqcn(MailingOpened))

    creates = counts.get('MailingClicked', 0)
    print("Clicks: %s" % creates)
    assert creates == stream.get(get_fqcn(MailingClicked))

    creates = counts.get('MailingShared', 0)
    print("Shares: %s" % creates)
    assert creates == stream.get(get_fqcn(MailingShared))

    creates = reduce(lambda x, y: x + y, counts.values(), 0)
    print("\nTotal: %s" % creates)
    assert creates == stream.get('total')

main()
