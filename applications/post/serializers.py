import owner as owner
from django.db.models import Avg
from rest_framework import serializers

from applications.post.models import Post, Category, Comment, Like, Rating, Image


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Comment
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    comments = CommentSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # print(instance.owner)
        # print(instance.images)
        rep['likes'] = instance.likes.filter(like=True).count()
        rep['rating'] = instance.ratings.all().aggregate(Avg('rating'))['rating__avg']
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        fiels_data = request.FILES
        post = Post.objects.create(**validated_data)

        # print('POST', post.id, post)
        post.save()
        for image in fiels_data.getlist('images'):
            Image.objects.create(post=post, image=image)
        return post






class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.parent:
            rep.pop('parent')
        return rep




class RatingSerializer(serializers.ModelSerializer):
    # owner = serializers.ReadOnlyField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Rating
        fields = ['rating']