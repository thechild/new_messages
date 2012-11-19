from django.db import models

# Create your models here.

class User(models.Model):
	first_name = models.CharField(max_length=100, blank=True)
	last_name = models.CharField(max_length=100, blank=True)
	primary_email = models.CharField(max_length=100, unique=True)
	primary_phone = models.CharField(max_length=25, blank=True)
	# will need some way to differentiate users who have accounts from those who are just included in groups/threads
	
	def groups(self):
		return Group.objects.filter(members__pk__exact=self.pk)

	def threads(self):
		return Thread.objects.filter(group__in=self.groups())

	def threads_sorted(self):
		return sorted(self.threads(), key=lambda t: t.newest_message_date(), reverse=True)

	def name(self):
		if self.first_name == '' and self.last_name == '':
			return self.primary_email
		else:
			return u'%s %s' % (self.first_name, self.last_name)

	def __unicode__(self):
		return self.name()

	
class Group(models.Model):
	name = models.CharField(max_length=100, blank=True)
	members = models.ManyToManyField(User)
	
	def non_blank_name(self):
		if self.name == '':
			return ', '.join(m.first_name for m in self.members.all())
		else:
			return self.name

	def member_count(self):
		return self.members.count()
	
	def threads(self):
		return Thread.objects.filter(group__pk__exact=self.pk)

	def threads_sorted(self):
		return sorted(self.threads(), key=lambda t: t.newest_message_date(), reverse=True)

	def __unicode__(self):
		return self.non_blank_name()

class Thread(models.Model):
	subject = models.CharField(max_length=1000)
	creator = models.ForeignKey(User)
	group = models.ForeignKey(Group) # A thread must be tied to a group
	creation_date = models.DateTimeField('date created', auto_now_add=True, blank=True)

	def members(self):
		return self.group.members.all()

	def messages(self):
		return Message.objects.filter(thread__pk__exact=self.pk)

	def newest_message_date(self):
		return self.messages()[0].pub_date

	def __unicode__(self):
		return self.subject

	class Meta:
		ordering = ('creation_date',)

class Message(models.Model):
	text = models.TextField()
	html = models.TextField(blank=True)
	sender = models.ForeignKey('User')
	pub_date = models.DateTimeField('date published', auto_now_add=True, blank=True)
	thread = models.ForeignKey('Thread') # A message must be tied to a thread

	def group(self):
		return self.thread.group

	def members(self):
		return self.thread.group.members

	def __unicode__(self):
		return self.text

	class Meta:
		ordering = ('pub_date',)

class ReadMessage(models.Model): # A ReadMessage is created when a user reads a message
	message = models.ForeignKey('Message')
	user = models.ForeignKey('User')
	date_read = models.DateTimeField('date read', auto_now_add=True, blank=True)

class ArchivedThread(models.Model): # An archivedThread is created when a user archives a thread - if the thread contains any newer messages the ArchivedThread is invalid
	thread = models.ForeignKey('Thread')
	user = models.ForeignKey('User')
	date_archived = models.DateTimeField('date archived', auto_now_add=True, blank=True)