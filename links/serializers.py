from django.utils import timezone
from rest_framework import serializers

from .models import Link
from .services import create_short_link


class URLSerializer(serializers.ModelSerializer):
    """
    Full detail serializer for a single Link.

    Used for retrieve and update endpoints.
    """
    full_short_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = [
            'id',
            'owner',
            'original_url',
            'short_code',
            'custom_alias',
            'created_at',
            'expires_at',
            'is_active',
            'click_count',
            'full_short_url',
            'is_expired',
        ]
        read_only_fields = [
            'id',
            'owner',
            'short_code',
            'created_at',
            'click_count',
            'full_short_url',
            'is_expired',
        ]

    def get_full_short_url(self, obj: Link) -> str:
        return obj.get_full_short_url()

    def get_is_expired(self, obj: Link) -> bool:
        return obj.is_expired()


class URLListSerializer(serializers.ModelSerializer):
    """
    Compact serializer used for list view.
    """
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
        ]

    def get_full_short_url(self, obj: Link) -> str:
        return obj.get_full_short_url()


class URLCreateSerializer(serializers.Serializer):
    """
    Serializer for creating short URLs.

    Uses service layer to handle:
    - URL validation
    - alias validation
    - short code generation
    - collision handling
    """
    original_url = serializers.CharField()
    custom_alias = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        """
        Cross-field validation hook if needed later.
        For now we just pass through.
        """
        return attrs

    def create(self, validated_data):
        """
        Create a Link using the service layer.

        The owner comes from the view (request.user),
        provided via serializer.save(owner=...).
        """
        owner = self.context['owner']

        original_url = validated_data.get('original_url')
        custom_alias = validated_data.get('custom_alias') or None
        expires_at = validated_data.get('expires_at')

        link = create_short_link(
            owner=owner,
            original_url=original_url,
            custom_alias=custom_alias,
            expires_at=expires_at,
        )
        return link