from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category_name(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name



class Story(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    Title = models.CharField(max_length=500)
    Author = models.CharField(max_length=300)
    Category = models.ForeignKey(Category_name, on_delete=models.SET_NULL, null=True, blank=True)
    Content = models.TextField()
    rating = models.FloatField(default=0)

    def update_average_rating(self):
        # Get all ratings related to this story
        ratings = Rating.objects.filter(story=self)

        # Calculate the total sum of ratings and the count of ratings
        total_sum = sum([rating.value for rating in ratings])
        ratings_count = ratings.count()

        # Calculate the average rating and update the rating field
        self.rating = total_sum / ratings_count if ratings_count > 0 else 0
        self.save()

    def __str__(self):
        return self.Title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5

    class Meta:
        unique_together = (('user', 'story'),)  # Each user can rate a story only once

    def __str__(self):
        return f'{self.user.username} rated {self.story.Title} {self.value} stars'


class Mywords(models.Model):
    word = models.CharField(max_length=100)
    meaning = models.TextField()

    def __str__(self):
        return self.word




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    following = models.ManyToManyField(User, related_name='followers', blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
