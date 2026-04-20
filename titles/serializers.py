from rest_framework import serializers
from .models import Title

class TitleSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Title
        fields = "__all__"