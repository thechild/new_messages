from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from Messages.models import User, Group, Thread, Message
from django import forms

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

#############################
#### View Only Functions ####
#############################

def user_messages(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	return render_to_response('user_detail.html', {'user': user}, context_instance=RequestContext(request))

def view_thread_as_user(request, user_id, thread_id):
	user = get_object_or_404(User, pk=user_id)
	thread = get_object_or_404(Thread, pk=thread_id)
	if not thread.user_has_access(user):
		return HttpResponseForbidden('You do not have access to that thread') # prob change this to a 404 at some point
	return render_to_response('thread_detail.html', {'user': user, 'thread': thread},
		context_instance=RequestContext(request))

def view_group_as_user(request, user_id, group_id):
	user = get_object_or_404(User, pk=user_id)
	group = get_object_or_404(Group, pk=group_id)

	if not group.user_has_access(user):
		return HttpResponseForbidden('You do not have access to that group') # prob change this to a 404 at some point

	# related groups
	r_groups = Group.objects.filter(members = user).exclude(pk = group.pk)
	for m in group.members.exclude(pk = user.pk):
		r_groups = r_groups.filter(members = m)

	return render_to_response('group_detail.html', {'user': user, 'group': group, 'related_groups': r_groups},
		context_instance=RequestContext(request))

##########################
#### Creation Methods ####
##########################

def new_message(request, user_id, thread_id):
	user = get_object_or_404(User, pk=user_id)
	thread = get_object_or_404(Thread, pk=thread_id)
	message_text = request.POST['message_text']
	message = Message(sender = user, thread = thread, text = message_text, html = message_text)
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

# Return an existing or new group with the given members (including creator)
def group_with_members(creator, members):
	
	groups = Group.objects.filter(members=members).filter(members=creator)
	group = []

	for g in groups:
		if g.members.count() == members.count() + 1: # find the one that's an exact match.  Should be a better DB way to do this...
			group = g

	if not group:
		# couldn't find this exact group, so create one
		group = Group()
		group.save()
		group.members.add(creator)
		for m in members:
			group.members.add(m)
		group.save()

	return group

def edit_group(request, user_id, group_id):
	user = get_object_or_404(User, pk=user_id)
	group = get_object_or_404(Group, pk=group_id)
	if request.method == 'POST':
		new_name = request.POST['group_name']
		group.name = new_name
		group.save()
		return HttpResponseRedirect(reverse('group_detail', args=(user.pk, group.pk,)))
	else:
		return HttpResponseForbidden("You can't edit a group directly.")

def new_thread(request, user_id):
	user = get_object_or_404(User, pk=user_id)
	users = User.objects.all().exclude(pk=user_id) # all users except for the logged in one.  Obviously this needs to get smarter!
	if request.method == 'POST':
		print 'we posted'
		form = ThreadForm(user, request.POST)
		if form.is_valid():
			print 'form is valid'
			members = User.objects.filter(pk__in=form.cleaned_data['members'])
			#members = [User.objects.get(pk=m) for m in form.cleaned_data['members']]
			print members

			group = group_with_members(user, members)
			thread = Thread(subject = form.cleaned_data['subject'],
							creator = user,
							group = group)
			thread.save()

			# finally add the message
			message = Message(sender = user,
							  text = form.cleaned_data['message_text'],
							  html = form.cleaned_data['message_text'],
							  thread = thread)
			message.save()

			return HttpResponseRedirect(reverse('thread_detail', args=(user.pk, thread.pk,)))
		else:
			print 'form invalid'
	else:
		form = ThreadForm(user)

	return render(request, 'new_thread.html', {'user': user, 'form': form})