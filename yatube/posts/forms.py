from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    text = forms.CharField(label='Текст поста', widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Введите текст коментария', }
