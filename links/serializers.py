from rest_framework import serializers
from .models import Link
from .services import create_short_link


class URLSerializer(serializers.ModelSerializer):
    full_short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = [
            'id',
            'original_url',
            'short_code',
            'custom_alias',
            'full_short_url',
            'click_count',
            'created_at',
            'expires_at',
            'is_active',
            'qr_code_image',
        ]
        read_only_fields = ['id', 'short_code', 'click_count', 'created_at', 'qr_code_image']

    def get_full_short_url(self, obj):
        return obj.get_full_short_url()


class URLListSerializer(serializers.ModelSerializer):
    full_short_url = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = [
            'id',
            'short_code',
            'custom_alias',
            'full_short_url',
            'click_count',
            'created_at',
            'expires_at',
            'is_active',
            'qr_code_image',
        ]

    def get_full_short_url(self, obj):
        return obj.get_full_short_url()


class URLCreateSerializer(serializers.Serializer):
    original_url = serializers.URLField()
    custom_alias = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def create(self, validated_data):
        request = self.context['request']
        return create_short_link(
            owner=request.user,
            original_url=validated_data['original_url'],
            custom_alias=validated_data.get('custom_alias'),
            expires_at=validated_data.get('expires_at'),
        )

    def to_representation(self, instance):
        return URLSerializer(instance, context=self.context).data