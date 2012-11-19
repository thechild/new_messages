from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from Messages.models import User, Group, Thread, Message
from django import forms

def user_messages(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render_to_response('user_detail.html', {'user': user}, context_instance=RequestContext(request))

def view_thread_as_user(request, user_id, thread_id):
	user = get_object_or_404(User, pk=user_id)
	thread = get_object_or_404(Thread, pk=thread_id)
	return render_to_response('thread_detail.html', {'user': user, 'thread': thread},
		context_instance=RequestContext(request))

def view_group_as_user(request, user_id, group_id):
	user = get_object_or_404(User, pk=user_id)
	group = get_object_or_404(Group, pk=group_id)
	return render_to_response('group_detail.html', {'user': user, 'group': group},
		context_instance=RequestContext(request))

def new_message(request, user_id, thread_id):
	user = get_object_or_404(User, pk=user_id)
	thread = get_object_or_404(Thread, pk=thread_id)
	message_text = request.POST['message_text']

	message = Message()
	message.sender = user
	message.thread = thread
	message.text = message_text
	message.html = message_text
	message.save()
	return HttpResponseRedirect(reverse('thread_detail', args=(user_id, thread_id,)))

def new_member(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	if request.method == 'POST':
		# create a new member
		f = UserForm(request.POST)
		if f.is_valid():
			new_member = f.save()
			return HttpResponseRedirect(reverse('new_thread', args=(user.pk, )))
		else:
			return render_to_response('new_member.html',
				{'user': user, 'form': f},
				context_instance=RequestContext(request))
	else:
		return render_to_response('new_member.html',
			{'user': user, 'form': UserForm() },
			context_instance=RequestContext(request))

class UserForm(forms.ModelForm):
	class Meta:
		model = User

class ThreadForm(forms.Form):
	def __init__(self, user, *args, **kwargs):
		super(ThreadForm, self).__init__(*args, **kwargs)
		users = User.objects.all().exclude(pk=user.pk)
		
		self.fields['members'] = forms.MultipleChoiceField(
			widget=forms.CheckboxSelectMultiple,
			choices=[ (u.pk, u.name()) for u in users])

	members = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
	subject = forms.CharField(max_length=100)
	message_text = forms.CharField(widget=forms.Textarea)

# this logic really shouldn't live here!
def new_thread(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	users = User.objects.all().exclude(pk=user_id)
	if request.method == 'POST':
		print 'we posted'
		form = ThreadForm(user, request.POST)
		if form.is_valid():
			print 'form is valid'
			members = [User.objects.get(pk=m) for m in form.cleaned_data['members']]
			print members

			group = Group.objects.filter(members=user)
			print 'group: %s' % group
			for m in members:
				group = group.filter(members=m)
				if group == []:
					print 'breaking'
					break

			if group.count() == 0:
				group = Group()
				group.creator = user
				group.save()
				group.members.add(user)
				for m in members:
					group.members.add(m)
				print group.members.count()
				group.save()
			else:
				group = group[0]

			print 'group: %s' % group

			# now we have the group, so create the thread:

			thread = Thread()
			thread.subject = form.cleaned_data['subject']
			thread.creator = user
			thread.group = group
			thread.save()

			# finally add the message

			message = Message()
			message.sender = user
			message.text = form.cleaned_data['message_text']
			message.html = message.text
			message.thread = thread
			message.save()

			return HttpResponseRedirect(reverse('thread_detail', args=(user.pk, thread.pk,)))
		else:
			print 'form invalid'
	else:
		form = ThreadForm(user)

	return render(request, 'new_thread.html', {'user': user, 'form': form})
	#return render_to_response('new_thread.html', {'user': user, 'users': users}, context_instance=RequestContext(request))
