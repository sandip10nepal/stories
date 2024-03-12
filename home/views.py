from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import requests
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum
from django.urls import reverse



def home(request):
    category = Category_name.objects.all()
    all_stories = Story.objects.select_related('user').all().order_by('-id')
    paginator = Paginator(all_stories, 9)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)
    current_user = request.user

    # Get the list of usernames the current user is following
    if current_user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        following_usernames = user_profile.following.values_list('username', flat=True)
    else:
        following_usernames = []
    return render(request, 'index.html', {'stories': stories, 'category': category, 'current_user': current_user,
                                          'following_usernames': following_usernames})


def publish(request):
    if request.method == "POST":
        Title = request.POST['title']
        Author = request.POST['author']
        category_name = request.POST['category']  # This line might conflict with the imported Category model
        Content = request.POST['content']
        user = request.user

        category = Category_name.objects.get(name=category_name)
        Story.objects.create(
            Title=Title,
            Author=Author,
            Category=category,
            Content=Content,
            user=user
        ).save()

    views={}
    views['story'] = Story.objects.all()
    views['category'] = Category_name.objects.all()  # Ensure Category is used correctly here

    return render(request, 'publish.html', views)




def account(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.info(request, 'Username already taken')
            return redirect('/account')

        user = User.objects.create(
            first_name=first_name,
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()

        messages.info(request, 'Account created successfully')
        return redirect('/login')

    return render(request, 'login.html')



def login_page(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid Login Credentials')
            return redirect('/login')

        else:
            login(request, user)
            return redirect('/home')



    return render(request, 'login.html')


def logout_page(request):
    logout(request)
    return redirect('/login')


def category_detail(request, name):

    category = get_object_or_404(Category_name, name=name)
    story = Story.objects.filter(Category=category)
    category = Category_name.objects.all()
    name= name
    current_user = request.user

    # Get the list of usernames the current user is following
    if current_user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        following_usernames = user_profile.following.values_list('username', flat=True)
    else:
        following_usernames = []
    return render(request, 'test2.html', {'story': story, 'name': name, 'category': category, 'current_user': current_user, 'following_usernames': following_usernames})

def profile(request, username):
    views = {}
    # Retrieve the user whose profile is being viewed
    user = get_object_or_404(User, username=username)
    user_profile = UserProfile.objects.get(user=user)

    # Fetch profile details for the specified user
    views['user_profile'] = user_profile
    views['user'] = user
    views['story'] = Story.objects.filter(user=user)
    views['followers_count'] = user_profile.followers.count()
    views['following_count'] = user_profile.following.count()
    views['rating_count'] = Rating.objects.filter(story__user=user).aggregate(Sum('value'))['value__sum']
    views['category'] = Category_name.objects.all()
    return render(request, 'profile.html', views)


def readmore(request,id):
    story = get_object_or_404(Story, pk=id)
    category = Category_name.objects.all()
    ratings = Rating.objects.filter(story=story)
    current_user = request.user


    # Calculate the total sum of ratings and the count of ratings
    total_sum = sum([rating.value for rating in ratings])
    ratings_count = ratings.count()

    # Calculate the average rating for the story
    average_rating = total_sum / ratings_count if ratings_count > 0 else 0

    if current_user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        following_usernames = user_profile.following.values_list('username', flat=True)
    else:
        following_usernames = []

    if request.user.is_authenticated:
        user_ratings = story.ratings.filter(user=request.user)
    else:
        user_ratings = None  # User is not authenticated, set user_ratings to None or handle accordingly

    return render(request, 'readmore.html', {'story': story, 'user_ratings': user_ratings, 'category': category, 'average_rating': average_rating, 'current_user': current_user, 'following_usernames': following_usernames})



def submit_rating(request):
    if request.method == 'POST':
        story_id = request.POST.get('story_id')
        rating_value = request.POST.get('rating')
        user = request.user  # Get the current user

        try:
            story_obj = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return HttpResponseRedirect(reverse('content', args=[story_id]))

        # Check if the user has already rated the story
        try:
            rating = Rating.objects.get(user=user, story=story_obj)
            rating.value = rating_value
            rating.save()
        except Rating.DoesNotExist:
            # If the user has not rated the story, create a new rating
            rating = Rating.objects.create(user=user, story=story_obj, value=rating_value)

        # Recalculate average rating for the story
        story_obj.update_average_rating()

        # Redirect back to the content page with the story_id
        return HttpResponseRedirect(reverse('readmore', args=[story_id]))

    else:
        # If it's not a POST request, redirect to the referring page
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def follow_user(request, username):
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)

        # Add the user_to_follow to the following list of the current user's profile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.following.add(user_to_follow)

        # Update the followers list of the user being followed
        user_to_follow_profile, created = UserProfile.objects.get_or_create(user=user_to_follow)
        user_to_follow_profile.followers.add(request.user)

        # Redirect to a specific page or reload the current page
        return redirect('profile', username=username)  # Replace 'profile_page' with the appropriate URL name

    # Handle invalid requests (e.g., GET requests)
    return redirect('/')


def search(request):
    views = {}
    views['category'] = Category_name.objects.all()
    if request.method == 'GET':
        query = request.GET.get('query', '')
        if query != "":
            views['search_story'] = Story.objects.filter(Q(Title__icontains=query) | Q(user__username__icontains=query))
    return render(request, 'search.html', views)



def fetch_dictionary_meaning(word):
    url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes (4xx or 5xx)
        data = response.json()

        # Process data and return meanings as before
        # Your existing logic for parsing the response goes here
        if data:
            meanings = []
            for entry in data:
                entry_meanings = entry.get('meanings', [])
                for meaning in entry_meanings:
                    definitions = meaning.get('definitions', [])
                    for definition in definitions:
                        meanings.append({'definition': definition.get('definition')})
            return meanings
    except requests.exceptions.RequestException as e:
        print('Error fetching data:', e)
        # Return an empty list or handle the error as per your application's requirements
        return []

def dictionary(request):
    if request.method == 'POST':
        word = request.POST.get('word')

        if not word:
            context = {
                'error_message': 'Please enter a word.'
            }
            return render(request, 'index.html', context)

        meanings = fetch_dictionary_meaning(word)

        # Your existing logic to process meanings goes here

        context = {
            'word': word,
            'meaning': meanings[0] if meanings else {'definition': 'Meaning not found'},
        }
        searched_word = Mywords.objects.create(word=word, meaning=context['meaning']['definition'])
        searched_word.save()

        searched_words = Mywords.objects.all()
        context['searched_words'] = searched_words
        return render(request, 'dictionary.html', context)
    else:
        searched_words = Mywords.objects.all()
        context = {'searched_words': searched_words}
        return render(request, 'dictionary.html', context)

